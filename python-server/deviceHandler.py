class deviceHandler :

    def __init__(self, _device_list = None) :
        if (_device_list == None) :
            self.m_list = []
        else :
            self.m_list = _device_list

    def addDevice(self, _id, _type = None, _data = None) :
        if (_type == None) :
            self.m_list.append([_id, 0, 0])
        else :
            self.m_list.append([_id, _type, _data])

    def rmDevice(self, _id) :
        for i in range(0, len(self.m_list)) :
            if (self.m_list[i][0] == _id) :
                del self.m_list[i]
                return 0
        return -1

    def getDevice(self, _id) :
        for i in range(0, len(self.m_list)) :
            if (self.m_list[i][0] == _id) :
                return (0, self.m_list[i])
        return (-1, None)

    def setType(self, _id, _type) :
        for i in range(0, len(self.m_list)) :
            if (self.m_list[i][0] == _id) :
                self.m_list[i][1] = _type
                return 0
        return -1

    def getType(self, _id) :
        for i in range(0, len(self.m_list)) :
            if (self.m_list[i][0] == _id) :
                return (0, self.m_list[i][1])
        return (-1, None)

    def setData(self, _id, _data) :
        for i in range(0, len(self.m_list)) :
            if (self.m_list[i][0] == _id) :
                self.m_list[i][2] = _data
                return 0
        return -1

    def getData(self, _id) :
        for i in range(0, len(self.m_list)) :
            if (self.m_list[i][0] == _id) :
                return (0, self.m_list[i][2])
        return (-1, None)

    def getList(self) :
        device_list = []
        for i in range(0, len(self.m_list)) :
            device_list.append([self.m_list[i][0], str(self.m_list[i][1]), str(self.m_list[i][0])])

        return device_list