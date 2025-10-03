# # load.py - simulate CPU stress
# import multiprocessing, math, time

# def busy(t):
#     end = time.time() + t
#     while time.time() < end:
#         math.factorial(50000)  # heavy computation

# if __name__ == "__main__":
#     procs = []
#     for _ in range(multiprocessing.cpu_count()):
#         p = multiprocessing.Process(target=busy, args=(30,))
#         p.start()
#         procs.append(p)

#     for p in procs:
#         p.join()
