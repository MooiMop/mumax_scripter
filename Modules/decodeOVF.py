import numpy as np
import struct

def _binaryDecode(filehandle, byteLength, decoder, targetarray, headers):
    for k in range(int(headers["znodes"])):
        for j in range(int(headers["ynodes"])):
            for i in range(int(headers["xnodes"])):
                for coord in range(3):  # Slowly populate, coordinate by coordinate
                    targetarray[i, j, k, coord] = decoder.unpack(filehandle.read(byteLength))[0]
    #print("Decode complete.")
    return (targetarray, headers)


def unpackFile(filename):
    headers = {}

    with open(filename, 'rb') as f:
        a = ""

        while not "Begin: Data" in a:
            a = str(f.readline().strip())

            for key in ["xbase", "ybase", "zbase", "xstepsize", "ystepsize", "zstepsize", "xnodes", "ynodes", "znodes",
                        "valuemultiplier"]:
                if key in a:
                    headers[key] = a.split(":")[1][:-1]
        outArray = np.zeros((int(headers["xnodes"]), int(headers["ynodes"]), int(headers["znodes"]),3))

        #decode = a.split(": ")[1][:-1]

        ''' #dedub stuff
        print("Data indicator: ", decode)
        print("only working for binary 8 currently ")
        binary = int(decode.split(" ")[2])
        endianflag = f.read(binary)
        print(endianflag)
        #print(struct.calcsize(endianflag))
        print(struct.unpack("f", endianflag)[0])
        '''

        dc = struct.Struct("f")
        target = _binaryDecode(f, 4, dc, outArray, headers)


    #return target, [headers["xstepsize"],headers["ystepsize"],headers["zstepsize"]]
    #return target[0],target[1] #header seems redundant, all information can be obtained from target[1]
    return target[0], target[1]
