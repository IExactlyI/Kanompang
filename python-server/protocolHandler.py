class protocolHandler :

    IDLE_STATE = 0
    GETID_STATE = 1
    GETTYPE_STATE = 2
    GETDATA_STATE = 3
    ENDING_STATE = 4

    def __init__(self) :
        self.protocol_state = self.IDLE_STATE
        self.protocol_id = 0
        self.protocol_type = 0
        self.protocol_data = 0

    def getID(self) :
        return self.protocol_id

    def getType(self) :
        return self.protocol_type

    def getData(self) :
        return self.protocol_data

    def processData(self,raw_byte) :

        if (self.protocol_state == self.IDLE_STATE) :
            if (raw_byte == 0x7E) :
                self.protocol_state = self.GETID_STATE
        elif (self.protocol_state == self.GETID_STATE) :
            print "Get into GETID_STATE"
            #Check for 0x7E is detection fault on last 0x7E
            if (raw_byte == 0x7E) :
                print "Found consecutive 0x7E set STATE to GETID_STATE"
                self.protocol_state = self.GETID_STATE;
                return 0

            self.protocol_id = raw_byte
            self.protocol_state = self.GETTYPE_STATE

        elif (self.protocol_state == self.GETTYPE_STATE) :
            print "Get into GETTYPE_STATE"
            if (raw_byte == 0x7E) :
                print "Found unknown 0x7E set STATE to IDLE_STATE"
                self.protocol_state = self.IDLE_STATE
                return -1

            self.protocol_type = raw_byte
            self.protocol_state = self.GETDATA_STATE

        elif (self.protocol_state == self.GETDATA_STATE) :
            print "Get into GETDATA_STATE"
            if (raw_byte == 0x7E) :
                print "Found unknown 0x7E set STATE to IDLE_STATE"
                self.protocol_state = self.IDLE_STATE
                return -1

            self.protocol_data = raw_byte
            self.protocol_state = self.ENDING_STATE
            return 0

        elif (self.protocol_state == self.ENDING_STATE) :
            print "Get into ENDING_STATE"
            if (raw_byte == 0x7E) :
                self.protocol_state = self.IDLE_STATE
                return 1

        return 0