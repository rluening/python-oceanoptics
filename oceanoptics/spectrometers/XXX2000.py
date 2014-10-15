# XXX: untested
#----------------------------------------------------------
from oceanoptics.base import OceanOpticsBase as _OOBase
from oceanoptics.defines import OceanOpticsError as _OOError
import time
import struct
#----------------------------------------------------------


class _XXX2000(_OOBase):

   def _build16bit(self,spec_raw):
        """ Despite saying 16 bit, max is 12bit due to ADC """
        r64=range(64)    
        spec=[0]*64*32
        k=0
        for i in range(32):
            for ii in r64:
                #t[i][ii]= MSB | LSB
                spec[k]=( ((spec_raw[2*i+1][ii])<<8) | spec_raw[2*i][ii] )
                k+=1
        return spec
        
    #Get a spectrum
    def _request_spectrum(self):
        self._usb_send(struct.pack('<B',0x09))
        time.sleep(self._integration_time/1000.00)
       # time.sleep(max(self._integration_time - self._USBTIMEOUT, 0))
        spec_raw = [[0]*64]*64
        for i in range(64):
           spec_raw[i] = self._usb_read( epi=0x82, epi_size=64)
        sync= self._usb_read( epi=0x82, epi_size=1)
        if sync[0] != 0x69:
            raise _OOError('request_spectrum: Wrong sync byte')
        #now sorting the data
        spectrum= self._build16bit(spec_raw)
        return spectrum
        
    def _query_information(self,index):
             self._usb_send(struct.pack('<BB',0x05,int(index)))
             tt=self._usb_read(epi=0x87, epi_size=17)
             info=tt[2:tt[2:].index(0)+2].tostring()
             return info


    def _set_integration_time(self, time_us):
        """ send command 0x02 """
        # XXX: The USB2000 requires the time set in Milliseconds!
        #      This overides the provided function of OOBase
        time_ms = int(time_us/1000)
        self._usb_send(struct.pack('<BH', 0x02,time_ms))
        
    def _query_status(self):
        """ 0xFE query status """
        # XXX: The USB2000 also returns the time in Milliseconds!
        #      This overides the provided function of OOBase
        #      and pretends to return us
        # XXX: query status does not actually return the usb_speed,
        #      but we return 0x00 to use the abstraction in OOBase

        ret = self._usb_query(struct.pack('<B', 0xFE))
        data = struct.unpack('<HHBBBBBBBBBBH', ret[:])
        pix, inte =struct.unpack('>H H', ret[0:4])
        ret2 = { 'pixels' : pix,
                'integration_time' :inte,
                'lamp_enable' : data[2],
                'trigger_mode' : data[3],
                'acquisition_status' : data[4],
                'Timer Swap' : data[5],
                'Spectral Data Ready' : data[6],
                'packets_in_endpoint' : 64,
                'usb_speed' : data[10] }
        return ret2    




class USB2000(_XXX2000):

    def __init__(self):
        super(USB2000, self).__init__('USB2000')

    


class HR2000(_XXX2000):

    def __init__(self):
        super(HR2000, self).__init__('HR2000')

   
