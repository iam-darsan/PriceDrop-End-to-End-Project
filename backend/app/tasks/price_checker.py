from celery import Task
from datetime import datetime
from sqlalchemy import func, text
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.product import Product
from app.models.price_alert import PriceAlert
from app.models.price_history import PriceHistory
from app.services.scraper_service import scraper_service
from app.services.email_service import email_service
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# Base Celery Task with DB
# -----------------------------
class DatabaseTask(Task):
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


# -----------------------------
# Price Checker Task
# -----------------------------
@celery_app.task(base=DatabaseTask, bind=True)
def check_prices(self):
    db = self.db

    try:
        now = datetime.utcnow()

        # ✅ FIX: Do datetime math in MySQL, not Python
        products = db.query(Product).filter(
            Product.is_active == True,
            (
                Product.last_checked_at.is_(None)
                |
                func.date_add(
                    Product.last_checked_at,
                    text("INTERVAL check_interval_minutes MINUTE")
                ) <= now
            )
        ).all()

        logger.info(f"Checking prices for {len(products)} products")

        for product in products:
            try:
                scraped_data = scraper_service.scrape_product(product.url)
                new_price = scraped_data["price"]

                # Save price history if price changed
                if new_price != product.current_price:
                    history = PriceHistory(
                        product_id=product.id,
                        price=new_price,
                        recorded_at=now
                    )
                    db.add(history)
                    product.current_price = new_price

                    logger.info(
                        f"Price updated for product {product.id}: {new_price}"
                    )

                product.last_checked_at = now

                # Fetch active alerts
                active_alerts = db.query(PriceAlert).filter(
                    PriceAlert.product_id == product.id,
                    PriceAlert.is_active == True,
                    PriceAlert.triggered_at.is_(None)
                ).all()

                for alert in active_alerts:
                    if new_price <= alert.target_price:
                        alert.triggered_at = now

                        send_email_notification.delay(
                            product_id=product.id,
                            alert_id=alert.id,
                            current_price=float(new_price)
                        )

                        logger.info(
                            f"Alert {alert.id} triggered for product {product.id}"
                        )

            except Exception as e:
                logger.error(
                    f"Error checking product {product.id}: {str(e)}"
                )
                continue

        # ✅ Single commit at the end (IMPORTANT)
        db.commit()

        logger.info(
            f"Price check completed for {len(products)} products"
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error in check_prices task: {str(e)}")
        raise


# -----------------------------
# Email Notification Task
# -----------------------------
@celery_app.task(base=DatabaseTask, bind=True)
def send_email_notification(self, product_id: int, alert_id: int, current_price: float):
    db = self.db

    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()

        if not product or not alert:
            logger.error(
                f"Product {product_id} or alert {alert_id} not found"
            )
            return

        user = product.user

        email_service.send_price_drop_notification(
            to_email=user.email,
            product_name=product.name or "Product",
            product_url=product.url,
            current_price=current_price,
            target_price=float(alert.target_price),
            currency=product.currency or "USD",
            image_url=product.image_url
        )

        logger.info(
            f"Email notification sent for product {product_id} to {user.email}"
        )

    except Exception as e:
        logger.error(f"Error sending email notification: {str(e)}")
        raise
