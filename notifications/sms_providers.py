import requests
from django.conf import settings
from typing import Optional


class MNotifySMSProvider:
    """
    mNotify SMS Provider for Ghana
    API Documentation: https://readthedocs.mnotify.com/
    Developer Portal: https://mnotifybms.com/developer/
    API Key Location: https://apps.mnotify.net/api/api
    """

    def __init__(self):
        self.api_key = settings.MNOTIFY_API_KEY
        self.sender_id = settings.MNOTIFY_SENDER_ID
        # mNotify API endpoint
        self.api_url = "https://apps.mnotify.com/sms/api"

    def send_sms(self, recipient_phone: str, message: str) -> dict:
        """
        Send SMS via mNotify API

        Args:
            recipient_phone: Phone number (format: 02XXXXXXXXX or +233XXXXXXXXX)
            message: SMS content

        Returns:
            dict with 'success' (bool) and 'message' (str)
        """
        try:
            # Validate inputs
            if not recipient_phone:
                return {
                    'success': False,
                    'message': 'Phone number is required',
                    'response': None
                }

            if not message:
                return {
                    'success': False,
                    'message': 'Message content is required',
                    'response': None
                }

            # Validate API key
            if not self.api_key or self.api_key == '':
                return {
                    'success': False,
                    'message': 'mNotify API key is not configured',
                    'response': None
                }

            # mNotify API endpoint pattern
            payload = {
                'key': self.api_key,
                'to': recipient_phone,
                'msg': message,
                'sender_id': self.sender_id,
            }

            response = requests.post(self.api_url, data=payload, timeout=10)

            # Try to parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                response_data = {'raw_response': response.text}

            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'SMS sent successfully',
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'message': response_data.get('message', 'Failed to send SMS'),
                    'response': response_data
                }

        except requests.RequestException as e:
            return {
                'success': False,
                'message': f'Network error: {str(e)}',
                'response': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'response': None
            }

    def check_balance(self) -> dict:
        """
        Check mNotify account SMS balance

        Returns:
            dict with balance information
        """
        try:
            if not self.api_key or self.api_key == '':
                return {
                    'success': False,
                    'message': 'mNotify API key is not configured'
                }

            payload = {
                'key': self.api_key,
                'action': 'check_balance'
            }

            response = requests.post(self.api_url, data=payload, timeout=10)

            if response.status_code == 200:
                try:
                    return {
                        'success': True,
                        'balance': response.json()
                    }
                except ValueError:
                    return {
                        'success': True,
                        'balance': {'raw_response': response.text}
                    }
            else:
                return {
                    'success': False,
                    'message': 'Failed to check balance'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
