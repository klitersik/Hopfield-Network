def hairpin(primer,head):
    tab_left = []
    tab_right = []
    maks = 0
    tmp = 0
    pairs = {"AT","TA","GC","CG"}
    for i in range(len(primer)):
        tmp_left = primer[:i+1]
        tmp_right = primer[i+1:]
        if len(tmp_left) - head >= 1 and len(tmp_right) - head >= 1:
            if len(tmp_left) <= len(tmp_right):
                for i in range(len(tmp_left)-head):
                    pair = tmp_left[i] + tmp_right[len(tmp_left)-i-1]
                    if pair in pairs:
                        #print(tmp_left,"-",tmp_right)
                        #print(pair)
                        maks = maks + 1
            elif len(tmp_left) > len(tmp_right):
                for i in range(head,len(tmp_right)):
                    pair = tmp_left[len(tmp_left)-i-1] + tmp_right[i]
                    if pair in pairs:
                        #print(tmp_left,tmp_right)
                        #print(pair)
                        maks = maks + 1
        if maks > tmp:
            tmp = maks
        maks = 0
    return tmp
c = 1
file = open("primers.txt", "r")
f = open("opd.txt", "w")
for line in file:
    hp = hairpin(line.strip(), 2)
    if hp > 0: 
        tmp = str(c) + "\t" + str(line.strip()) + "\t" + str(hp) + "\n"
        f.write(tmp)
    c += 1
file.close()
