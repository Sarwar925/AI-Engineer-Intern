import logging
import os

# 1. SETUP DIRECTORY AND LOGGER
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, "crash_report.log")

logging.basicConfig(
    level=logging.ERROR,
    filemode='a',
    filename=log_file,
    format='%(asctime)s - %(levelname)s\n%(message)s\n' + ('-'*20)
)

# 2. THE FUNCTION THAT WILL FAIL
def cause_a_real_error():
    # This will cause a 'ZeroDivisionError'
    return 10 / 0

# 3. EXECUTION & LOGGING
if __name__ == "__main__":
    try:
        print("Attempting to run the function...")
        cause_a_real_error()
    except Exception as e:
        # 'logging.exception' is the key: it logs the FULL error traceback
        logging.exception("A CRITICAL ERROR OCCURRED:")
        print(f"The program crashed! Details have been saved to {log_file}")