import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import logging
from typing import Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
    
    def _create_price_drop_email(
        self,
        product_name: str,
        product_url: str,
        current_price: Decimal,
        target_price: Decimal,
        currency: str,
        image_url: Optional[str] = None
    ) -> str:
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #4CAF50;">Price Drop Alert!</h2>
                    <p>Great news! The price has dropped on a product you're tracking.</p>
                    
                    <div style="margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-left: 4px solid #4CAF50;">
                        <h3 style="margin-top: 0;">{product_name}</h3>
                        {f'<img src="{image_url}" style="max-width: 200px; height: auto;" />' if image_url else ''}
                        <p style="font-size: 24px; color: #4CAF50; margin: 10px 0;">
                            <strong>{currency} {current_price}</strong>
                        </p>
                        <p style="color: #666;">
                            Target Price: {currency} {target_price}
                        </p>
                    </div>
                    
                    <a href="{product_url}" style="display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        View Product
                    </a>
                    
                    <p style="margin-top: 20px; font-size: 12px; color: #999;">
                        You received this email because you set up a price alert on our platform.
                    </p>
                </div>
            </body>
        </html>
        """
        return html
    
    def send_price_drop_notification(
        self,
        to_email: str,
        product_name: str,
        product_url: str,
        current_price: Decimal,
        target_price: Decimal,
        currency: str = "USD",
        image_url: Optional[str] = None
    ) -> bool:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Price Drop Alert: {product_name}"
            msg['From'] = self.email_from
            msg['To'] = to_email
            
            html_content = self._create_price_drop_email(
                product_name, product_url, current_price, target_price, currency, image_url
            )
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Price drop email sent to {to_email} for product {product_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

email_service = EmailService()
