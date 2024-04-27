from fe.bench.workload import Workload
from fe.bench.workload import NewOrder
from fe.bench.workload import Payment
from fe.bench.workload import CancelOrder
from fe.bench.workload import SendOrder
from fe.bench.workload import ReceiveOrder
import time
import threading


class Session(threading.Thread):
    def __init__(self, wl: Workload):
        threading.Thread.__init__(self)
        self.workload = wl
        self.new_order_request = []
        self.payment_request = []
        self.cancel_request=[]
        self.send_request=[]
        self.receive_request=[]
        self.payment_i = 0
        self.new_order_i = 0
        self.cancel_order_i=0
        self.send_order_i=0
        self.receive_order_i=0
        self.payment_ok = 0
        self.new_order_ok = 0
        self.cancel_order_ok=0
        self.send_order_ok=0
        self.receive_order_ok=0
        self.time_new_order = 0
        self.time_payment = 0
        self.time_cancelOrder=0
        self.time_sendOrder=0
        self.time_receiveOrder=0
        self.thread = None
        self.gen_procedure()

    def gen_procedure(self):
        for i in range(0, self.workload.procedure_per_session):
            new_order = self.workload.get_new_order()
            self.new_order_request.append(new_order)

    def run(self):
        self.run_gut()

    def run_gut(self):
        for new_order in self.new_order_request:
            before = time.time()
            ok, order_id = new_order.run()
            after = time.time()
            self.time_new_order = self.time_new_order + after - before
            self.new_order_i = self.new_order_i + 1
            if ok==200:
                self.new_order_ok = self.new_order_ok + 1
                payment = Payment(new_order.buyer, order_id,new_order.seller,new_order.store_id)
                self.payment_request.append(payment)
            else:
                self.workload.logging_print(ok)
                assert(0)
            if self.new_order_i % 100 ==0 or self.new_order_i == len(
                self.new_order_request
            ):
                for payment in self.payment_request:
                    #payment=Payment(payment)
                    before = time.time()
                    ok = payment.run()
                    after = time.time()
                    self.time_payment = self.time_payment + after - before
                    self.payment_i = self.payment_i + 1
                    if ok==200:
                        self.payment_ok = self.payment_ok + 1
                        if(self.payment_i%3==0):
                            cancel_order=CancelOrder(payment.buyer,payment.order_id,payment.seller,payment.store_id)
                            self.cancel_request.append(cancel_order)
                        else:
                            send_order=SendOrder(payment.seller,payment.order_id,payment.buyer,payment.store_id)
                            self.send_request.append(send_order)
                    else:
                        self.workload.logging_print(ok)
                        assert(0)
                self.payment_request = []
                for cancelOrder in self.cancel_request:
                    before = time.time()
                    ok = cancelOrder.run()
                    after = time.time()
                    self.time_cancelOrder = self.time_cancelOrder + after - before
                    self.cancel_order_i = self.cancel_order_i + 1
                    if ok==200:
                        self.cancel_order_ok = self.cancel_order_ok + 1
                    else:
                        self.workload.logging_print(ok)
                        self.workload.logging_print(order_id)
                        assert(0)
                self.cancel_request = []
                for sendOrder in self.send_request:
                    before = time.time()
                    ok = sendOrder.run()
                    after = time.time()
                    self.time_sendOrder = self.time_sendOrder + after - before
                    self.send_order_i = self.send_order_i + 1
                    if ok==200:
                        self.send_order_ok = self.send_order_ok + 1
                        receiveOrder=ReceiveOrder(sendOrder.buyer,sendOrder.order_id)
                        self.receive_request.append(receiveOrder)
                    else:
                        self.workload.logging_print(ok)
                        assert(0)
                self.send_request = []
                for receiveOrder in self.receive_request:
                    before = time.time()
                    ok = receiveOrder.run()
                    after = time.time()
                    self.time_receiveOrder = self.time_receiveOrder + after - before
                    self.receive_order_i = self.receive_order_i + 1
                    if ok==200:
                        self.receive_order_ok = self.receive_order_ok + 1
                    else:self.workload.logging_print(ok)
                self.receive_request=[]
                self.workload.update_stat(
                    self.new_order_i,
                    self.payment_i,
                    self.cancel_order_i,
                    self.send_order_i,
                    self.receive_order_i,
                    self.new_order_ok,
                    self.payment_ok,
                    self.cancel_order_ok,
                    self.send_order_ok,
                    self.receive_order_ok,
                    self.time_new_order,
                    self.time_payment,
                    self.time_cancelOrder,
                    self.time_sendOrder,
                    self.time_receiveOrder
                )
                
