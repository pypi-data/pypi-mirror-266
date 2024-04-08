class Electro:
    def __init__(self,charge1,charge2,distance):
        self.charge1=charge1
        self.charge2=charge2
        self.r=distance
    def Coulomb(self):
        Force=9*(10**9)*(self.charge1*self.charge2)/self.r**2
        return Force