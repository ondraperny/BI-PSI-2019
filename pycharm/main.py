import socket
import threading

KEY_SERVER = 54621
KEY_CLIENT = 45328

TIMEOUT = 1
TIMEOUT_RECHARGING = 5

SERVER_MOVE = b"102 MOVE\a\b"
SERVER_TURN_LEFT = b"103 TURN LEFT\a\b"
SERVER_TURN_RIGHT = b"104 TURN RIGHT\a\b"
SERVER_PICK_UP = b"105 GET MESSAGE\a\b"
SERVER_LOGOUT = b"106 LOGOUT\a\b"
SERVER_OK = b"200 OK\a\b"
SERVER_LOGIN_FAILED = b"300 LOGIN FAILED\a\b"
SERVER_SYNTAX_ERROR = b"301 SYNTAX ERROR\a\b"
SERVER_LOGIC_ERROR = b"302 LOGIC ERROR\a\b"

CLIENT_RECHARGING = b"RECHARGING"

HOST = '0.0.0.0'
PORT = 14781

class ServerService:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    socket.setdefaulttimeout(TIMEOUT)

    def waitForRequest(self):
        # start listening
        self.sock.listen()

        # start new thread for every connection
        while True:
            conn, address = self.sock.accept()
            newThread = threading.Thread(target=ClientService, args=(conn, address))
            newThread.start()

class ClientService:
    def __init__(self, conn, address):
        socket.setdefaulttimeout(TIMEOUT)

        print("Start thread for new connection.")
        self.dirOfRobot = 0 # top 0 right 1 bottom 2 left 3
        self.posX = 0
        self.posY = 0
        self.robotListening = True
        self.restOfMessage = "".encode()
        self.messageQueue = []
        self.conn = conn
        self.address = address

        # catching timeout exception, if exception appear, connection is closed
        try:
            self.auth()
        except:
            conn.close()

    def auth(self):
        read = self.readMessage(12)
        if not read:
            self.syntaxError()
            return False

        message = self.messageQueue.pop(0)
        if not message:
            self.conn.send(SERVER_LOGIN_FAILED)
            self.conn.close()
            return False

        tmpHash = (sum(message) * 1000) % 65536
        midHash = str((tmpHash + KEY_SERVER) % 65536)
        self.conn.send(str.encode(midHash) + "\a\b".encode())

        if not self.messageQueue:
            message = self.readMessage(7)
            if not message:
                self.syntaxError()
                return False
        message = self.messageQueue.pop(0)

        for i in message.decode():
            if not str(i).isdigit():
                self.syntaxError()
                return False

        clHash = (tmpHash + KEY_CLIENT) % 65536
        if str(clHash).encode() == message:
            self.conn.send(SERVER_OK)
        else:
            self.conn.send(SERVER_LOGIN_FAILED)
            self.conn.close()

        self.posX, self.posY, self.dirOfRobot = self.findPositionAndDirection()
        self.getRobotToStart(-2, -2)
        self.findSecret()

        self.conn.send(SERVER_LOGOUT)
        self.conn.close()

    def findPositionAndDirection(self):
        position = self.turnRobotRight()
        newPosition = self.moveWrapper()

        oldX = int(position[0])
        oldY = int(position[1])
        newX = int(newPosition[0])
        newY = int(newPosition[1])

        if newX > oldX:
            dirOfRobot = 1
        elif newX < oldX:
            dirOfRobot = 3
        elif newY > oldY:
            dirOfRobot = 0
        elif newY < oldY:
            dirOfRobot = 2

        print("Current position: " + str(newX) + " " + str(newY) + ", and direction: " + str(dirOfRobot))
        return int(newX), int(newY), int(dirOfRobot)

    def moveWrapper(self):
        self.conn.send(SERVER_MOVE)
        self.readMessage(12)
        newPosition = self.messageQueue.pop(0).split()

        print("Moving forward", newPosition)
        while int(self.posX) == int(newPosition[1]) and int(self.posY) == int(newPosition[2]):
            self.conn.send(SERVER_MOVE)
            self.readMessage(12)
            newPosition = self.messageQueue.pop(0).split()
            print("Moving forward(again - last signal was ignored by robot", newPosition)

        return newPosition[1], newPosition[2]

    def findSecret(self):
        for i in 0,1,2,3,4,9,8,7,6,5,10,11,12,13,14,15,16,17,18,19,24,23,22,21,20:
            x, y = self.numberToVertex(i)
            print("Robot is on way to: x = ",x - 2," y = ", y - 2)

            self.getRobotToStart(x - 2, y - 2)
            self.conn.send(SERVER_PICK_UP)

            if not len(self.messageQueue):
                read = self.readMessage(100)
                if not read:
                    self.syntaxError()
                    return False
            read = self.messageQueue.pop(0)

            if len(read) != 0:
                print("Secret message found: ", read)
                break
            else:
                print("Message not found, moving robot to another position")

    def readMessage(self, size):
        read = self.restOfMessage

        while True:
            read += self.conn.recv(512)
            if "\a\b".encode() not in read:
                # checking if alloved size of received messages is correct
                if len(read) >= size:
                    return False
            else:
                firstMessageLength = len(read.decode().split("\a\b")[0])
                # message length + 2 for \a\b
                if firstMessageLength + 2 > size \
                        and CLIENT_RECHARGING not in read:
                    return False
                else:
                    break

        for i in read.decode().split("\a\b")[:-1]:
            if i != "RECHARGING":
                self.messageQueue.append(i.encode())
            else:
                self.robotCharging()

        self.restOfMessage = read.decode().split("\a\b")[-1].encode()
        if self.robotListening:
            self.robotListening = False
            if not self.messageQueue:
                self.readMessage(size)
        return True

    # calculate coordinates from square number
    def numberToVertex(self, number):
        y = number // 5
        x = number % 5
        return x, y

    def getRobotToStart(self, startX, startY):
        while int(self.posX) != startX:
            if int(self.posX) > startX:
                self.turnRobotToDirection(3)
                self.posX, self.posY = self.moveWrapper()
            elif int(self.posX) < startX:
                self.turnRobotToDirection(1)
                self.posX, self.posY = self.moveWrapper()

        while int(self.posY) != startY:
            if int(self.posY) > startY:
                self.turnRobotToDirection(2)
                self.posX, self.posY = self.moveWrapper()
            elif int(self.posY) < startY:
                self.turnRobotToDirection(0)
                self.posX, self.posY = self.moveWrapper()


    def turnRobotRight(self):
        self.conn.send(SERVER_TURN_RIGHT)

        if not len(self.messageQueue):
            read = self.readMessage(12)
            if not read:
                self.syntaxError()
                return False

        string = self.messageQueue.pop(0)

        string = string[3:].decode()
        if not string[-1].isdigit():
            self.syntaxError()

        string = string.split(" ")
        x = string[0]
        y = string[1]
        try:
            return int(x), int(y)
        except:
            self.syntaxError()

    def robotCharging(self):
        tmp = "".encode()
        self.conn.settimeout(TIMEOUT_RECHARGING)
        if CLIENT_RECHARGING in self.messageQueue:
            self.messageQueue.remove(CLIENT_RECHARGING)

        while True:
            tmp += self.conn.recv(12)

            if "FULL POWER\a\b".encode() in tmp:
                self.robotListening = True
                if len(tmp) > 12:
                    # copy remainder of message
                    self.restOfMessage += tmp[13:]
                self.conn.settimeout(TIMEOUT)
                return True
            if tmp[:12] not in "FULL POWER\a\b".encode():
                self.conn.send(SERVER_LOGIC_ERROR)
                self.conn.close()
                return False

    def turnRobotToDirection(self, newDirection):
        while int(self.dirOfRobot) != int(newDirection):
            self.turnRobotRight()
            self.dirOfRobot = ((self.dirOfRobot + 1) % 4)
            print("Turning robot to right", self.dirOfRobot)

    def syntaxError(self):
        self.conn.send(SERVER_SYNTAX_ERROR)
        self.conn.close()

ServerService().waitForRequest()
