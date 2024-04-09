def write_to_log(log_path, my_text):
    
    import datetime
            
    # create output text
    output_text = datetime.datetime.now().strftime("%d/%m/%Y: %H:%M:%S") + ': ' + my_text
    
    # print to screen
    print(output_text)
    
    # write to log
    log_file = open(log_path, 'a')
    log_file.write(output_text + '\n')
    log_file.close()