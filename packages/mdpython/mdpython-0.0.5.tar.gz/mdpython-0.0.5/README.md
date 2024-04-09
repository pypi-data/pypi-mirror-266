# MD Python Library

This package contains high level functions for common Python use cases.

# Compare Directories

   

    from mdpython.fileutils import compare  
      
    cmp = compare.compare_dirs(r"C:\Users\Dell\OneDrive\Desktop\result_9th",  
                               r"C:\Users\Dell\OneDrive\Desktop\result_9th_v2")  
      
    cmp.gen_html_report(r"C:\Users\Dell\OneDrive\Desktop\out.html", ["py", "txt",  
                                                                     "json"])  
      
    for fl in cmp.files_only_in_right:  
        if fl.name.endswith("py"):  
            print(fl.absolute())


# Menu based app

    from datetime import datetime
    from random import randint, choice
    from mdpython.uiutils import menu_based_app
    
    def show_date():
        print(datetime.now().strftime("%Y-%m-%d"))
    
    
    def show_time():
        print(datetime.now().strftime("%H:%M:%S"))
    
    
    def show_date_and_time():
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    
    def show_random_number():
        print(randint(1, 100))
    
    
    def show_random_color():
        print(choice(['red', 'blue', 'green']))
    
    
    ar = [
        ["Random", "Random Integer", show_random_number],
        ["Random", "Random Color", show_random_color],
        ["Date", "Show Date", show_date],
        ["Date", "Show Time", show_time],
        ["Date", "Show Date and Time", show_date_and_time]
    ]
    
    menu_based_app.start(ar)

# Disk cleanup

    from mdpython.fileutils import cleanup
    
    dr = r"C:\Users\Dell\OneDrive\Desktop\result_9th"
    
    info = cleanup.retrieve_info(dr)
    
    print("sorted by time")
    for dtl in info.sort_by_time()[:5]:
        print(dtl)
    
    print("\nsorted by size")
    for dtl in info.sort_by_size()[:5]:
        print(dtl)
    
    print("\nmodified in last 30 mins")
    for dtl in info.modified_within(mins=30)[:5]:
        print(dtl)
    
    print("\nmodified more than 1 day ago")
    for dtl in info.modified_before(mins=24 * 60)[:5]:
        print(dtl)
    
    print("\nsorted by number of files in directory")
    for dtl in info.sort_by_file_count()[:5]:
        print(dtl)

# Getting execution duration

    from mdpython.debugutils import timer
    from random import randint
    from math import factorial
    
    timer.start("main")
    
    def count_elements_in_array():
        ar = list(range(randint(1000000,10000000)))
        print(len(ar))
    
    def get_factorial():
        for i in range(5):
            timer.start("looptest")
            num = randint(900,1000)
            print(num, factorial(num))
            timer.stop("looptest")
    
    timer.start("func1")
    count_elements_in_array()
    timer.stop("func1")
    
    get_factorial()
    
    timer.stop("main")
    
    timer.show()

    -- Output
    Name                           Duration             Start Time           End Time            
    ============================== ==================== ==================== ====================
    main                           0:00:00.046207       2024-04-08 21:24:59  2024-04-08 21:24:59 
    func1                          0:00:00.033129       2024-04-08 21:24:59  2024-04-08 21:24:59 
    looptest.4                     0:00:00.010020       2024-04-08 21:24:59  2024-04-08 21:24:59 
    looptest.2                     0:00:00.003058       2024-04-08 21:24:59  2024-04-08 21:24:59 
    looptest.1                     0:00:00              2024-04-08 21:24:59  2024-04-08 21:24:59 
    looptest.3                     0:00:00              2024-04-08 21:24:59  2024-04-08 21:24:59 
    looptest.5                     0:00:00              2024-04-08 21:24:59  2024-04-08 21:24:59 
