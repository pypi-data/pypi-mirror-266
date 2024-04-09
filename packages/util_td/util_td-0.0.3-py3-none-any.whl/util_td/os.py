import signal
import sys
 
def on_ctrlc(cb):
    # 自定义信号处理函数
    def my_handler(signum, frame):
        global stop
        stop = True
        print("程序被手动终止.")
        cb()
        sys.exit()
    
    
    # 设置相应信号处理的handler
    signal.signal(signal.SIGINT, my_handler)    #读取Ctrl+c信号
   
def clear_input_buffer():
    if sys.stdin.isatty():
        try:
            import termios
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)
        except ImportError:
            # fallback for Windows
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()

    # 调用该函数以清空输入缓冲区