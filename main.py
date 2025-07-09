# main.py
import functions_framework
from binance_monitor_gcp import BinanceTwitterMonitor
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def main(request):
    """
    Cloud Functions HTTP 觸發器
    """
    try:
        logger.info("開始執行 Binance Twitter 監控")
        
        # 建立監控器實例
        monitor = BinanceTwitterMonitor()
        
        # 執行一次監控
        result = monitor.run_monitor_once()
        
        logger.info(f"監控執行完成: {result}")
        
        return {
            'statusCode': 200,
            'body': result
        }
        
    except Exception as e:
        logger.error(f"Cloud Function 執行失敗: {str(e)}")
        return {
            'statusCode': 500,
            'body': {
                'success': False,
                'message': f'執行失敗: {str(e)}'
            }
        }

# 如果是由 Cloud Scheduler 觸發（推薦方式）
@functions_framework.cloud_event
def scheduled_main(cloud_event):
    """
    Cloud Scheduler 觸發器（推薦使用）
    """
    try:
        logger.info("Cloud Scheduler 觸發 Binance Twitter 監控")
        
        # 建立監控器實例
        monitor = BinanceTwitterMonitor()
        
        # 執行一次監控
        result = monitor.run_monitor_once()
        
        logger.info(f"監控執行完成: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Cloud Function 執行失敗: {str(e)}")
        raise e