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
