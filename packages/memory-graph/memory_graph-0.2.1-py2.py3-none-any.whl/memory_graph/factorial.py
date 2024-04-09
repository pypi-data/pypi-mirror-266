import memory_graph

def factorial(n):
    if n==0:
        return 1
    #memory_graph.show( memory_graph.get_call_stack(), block=True )
    result = n*factorial(n-1)
    #memory_graph.show( memory_graph.get_call_stack(), block=True )
    return result

factorial(20)