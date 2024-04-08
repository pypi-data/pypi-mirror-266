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
