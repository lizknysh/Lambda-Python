import json 
import logging 
  
logger = logging.getLogger() 
logger.setLevel(logging.INFO) 
  
  
def lambda_handler(event, context): 
    for record in event["Records"]: 
        message_id = record["messageId"] 
        attempts = record.get("attributes", {}).get( 
            "ApproximateReceiveCount", "unknown" 
        ) 
        logger.info("Received %s attempt %s", message_id, attempts) 
  
        order = json.loads(record["body"]) 
        if order.get("simulate_failure", False): 
            raise ValueError("Intentional MCIT lab failure") 
  
        logger.info( 
            "Processed order %s | customer=%s | item=%s", 
            order["order_id"], order["customer"], order["item"] 
        ) 
  
    return {"status": "done"} 