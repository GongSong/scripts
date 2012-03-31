def ex_83():
    '''
    使用range函数生成下面的列表
    
    (a) [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    (b) [3, 6, 9, 12, 15, 18]
    (c) [-20, 200, 420, 640, 860]
    >>> ex_83()
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    [3, 6, 9, 12, 15, 18]
    [-20, 200, 420, 640, 860]
    '''
    print range(10)
    print range(3,21,3)
    print range(-20,1080,220)

if __name__ == "__main__":
    import doctest
    doctest.testmod()