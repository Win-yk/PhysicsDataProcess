import io, os
import math
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from tkinter import messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import numpy as np
import torch

class MeasureProcess(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        self.title = tk.Label(self, text = '使用格拉布斯准则处理异常数据，并求出误差（不确定度）')
        self.title.grid(row = 0, column = 0)
        
        class AlphaChoose(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                tips = tk.Label(self, text = '选择显著水平（危险率）α')
                tips.grid(row = 0, column = 0)
                
                cbox = ttk.Combobox(self, values = ('0.05', '0.01'), takefocus = False)
                cbox.current(0)
                cbox.grid(row = 0, column = 1)
                self.get_alpha = lambda: int(cbox.get() == '0.01')
        self.alpha_choose = AlphaChoose(self)
        self.alpha_choose.grid(row = 1, column = 0)
        
        class NInput(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                tips = tk.Label(self, text = '输入测量次数 n（3~20之间）')
                tips.grid(row = 0, column = 0)
                
                entry = tk.Entry(self, exportselection = False)
                entry.delete(0, "end")
                entry.insert(0, '0')
                entry.grid(row = 0, column = 1)
                self.get_n = lambda: int(entry.get().strip())
        self.n_input = NInput(self)
        self.n_input.grid(row = 1, column = 1)
        
        class InstrumentPara(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                tips = tk.Label(self, text = '仪器误差限 Δ仪（仪器最小分度值 ÷ 2）')
                tips.grid(row = 0, column = 0)
                
                entry = tk.Entry(self, exportselection = False)
                entry.delete(0, "end")
                entry.insert(0, '1.000000')
                entry.grid(row = 0, column = 1)
                
                self.get_delta = entry.get
        self.instrument_para = InstrumentPara(self)
        self.instrument_para.grid(row = 2, column = 0)
        
        class UBInput(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                tips = tk.Label(self, text = '【忽略】仪器误差（不确定度）u_B')
                tips.grid(row = 0, column = 0)
                
                entry = tk.Entry(self, exportselection = False)
                entry.delete(0, "end")
                entry.insert(0, '0.288675')
                entry.grid(row = 0, column = 1)
                
                self.get_ub = entry.get
        self.ub_input = UBInput(self)
        self.ub_input.grid(row = 2, column = 1)
        
        class ValueInput(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                self.get_value = []
                for i in range(20):
                    tip = tk.Label(self, text = f'第{i+1}次')
                    tip.grid(row = i, column = 0)
                    
                    entry = tk.Entry(self, exportselection = False)
                    entry.delete(0, "end")
                    entry.grid(row = i, column = 1)
                    self.get_value.append(entry.get)
        self.value_input = ValueInput(self)
        self.value_input.grid(row = 3, column = 0)
        
        self.answer = tk.Text(self, undo = True, autoseparators = False)
        self.answer.grid(row = 3, column = 1)
        
        class StartButton(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                btn = tk.Button(self, text = '开始计算', command = master.calc)
                btn.grid(row = 0, column = 0)
        start_button = StartButton(self)
        start_button.grid(row = 0, column = 1)
        
    def calc(self):
        try:
            g0VALUE = [[1.15, 1.46, 1.67, 1.82, 1.94, 2.03, 2.11, 2.18, 2.23, 2.28, 2.33, 2.37, 2.41, 2.44, 2.48, 2.50, 2.53, 2.56], 
                       [1.16, 1.49, 1.75, 1.94, 2.10, 2.22, 2.32, 2.41, 2.48, 2.55, 2.61, 2.66, 2.70, 2.75, 2.78, 2.82, 2.85, 2.88]]
            alpha_type = self.alpha_choose.get_alpha()
            n = self.n_input.get_n()
            ub = float(self.instrument_para.get_delta())/math.sqrt(3) if self.instrument_para.get_delta() else float(self.ub_input.get_ub())
            mx = ub * math.sqrt(3)
            
            
            if n not in range(3, 21):
                raise
            try:
                value = [float(self.value_input.get_value[i]().strip()) for i in range(n)]
            except:
                value = [float(self.answer.get(f'{i+1}.0', f'{i+1}.999').strip()) for i in range(n)]
            
            self.answer.delete(1.0, 'end')
            
            while n >= 3:
                g0 = g0VALUE[alpha_type][n - 3]
                
                avg = 0.0
                for x in value:
                    avg += x
                avg /= n
                avg = round(avg, -math.floor(math.log10(mx)))
                
                sig = 0.0
                for x in value:
                    sig += (x - avg) ** 2
                sig = math.sqrt(sig / (n - 1))
                #v = math.floor(math.log10(mx))
                #if sig < (10 ** v) * 3:
                #    v -= 1
                #sig = math.ceil(sig * (10 ** -v)) * (10 ** v)
                
                self.answer.insert('insert', f'正在进行格拉布斯准则检验，当前 n 为 {n}，g0 为 {g0}，平均值为 {avg}，标准差为 {sig}\n')
                
                arr = value.copy()
                for x in value:
                    gi = abs(x - avg) / sig
                    if gi > g0:
                        self.answer.insert('insert', f'当前 gi 为 {gi}，剔除异常数据{x}\n')
                        arr.remove(x)
                
                if len(value) == len(arr):
                    break
                value = arr
                n = len(value)
            
            ua = sig / math.sqrt(n)
            u = math.sqrt(ua ** 2 + ub ** 2)
            v = float('%.1g'%u)
            u = v if v > u else float('%.1g'%(v + 10 ** math.floor(math.log10(v))))
            avg = round(avg, -math.floor(math.log10(u)))
            self.answer.insert('insert', f'测量结果为{avg}±{u}')
            
        except:
            messagebox.showerror(title = '错误', message = '计算过程出现问题，请检查输入是否有误！')
                

class DataCalculate(tk.Frame):
    
    TIP_STR = '''示例：sqrt(exp(b ** 2)/a)
可用函数：
abs(x)   --- x 的绝对值
sqrt(x)  --- x 的二次根
exp(x)   --- e 的 x 次方
ln(x)    --- ln x
lg(x)    --- lg x
sin(x)   --- sin x
cos(x)   --- cos x
tan(x)   --- tan x
asin(x)  --- arcsin x
acos(x)  --- arccos x
atan(x)  --- arctan x
可用运算符：
x + y  --- x 加 y
x - y  --- x 减 y
x * y  --- x 乘 y
x / y  --- x 除以 y
(x)    --- 强调优先级（只能使用小括号，但可以嵌套）
x ** y --- x 的 y 次方
PS：
由于某些原因，请自行将最后结果转化为科学计数法
并保留适量的末尾 0
PS2：
常数请自行选择合适的保留位数填入（尽量多，如 3.1415926）'''
    
    def __init__(self, master):
        super().__init__(master)
        
        self.title = tk.Label(self, text = '通过有效数字运算法则和标准误差传递公式计算数据的计算器')
        self.title.grid(row = 0, column = 0)
        
        self.tips = tk.Label(self, text = self.TIP_STR)
        self.tips.grid(row = 1, column = 0)
        
        class ValueInput(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                VALUE_NAME = ['a', 'b', 'c', 'd', 'e']
                self.get_value = []
                for i in range(5):
                    tip = tk.Label(self, text = f'{VALUE_NAME[i]} = ')
                    tip.grid(row = i, column = 0)
                    
                    entry1 = tk.Entry(self, exportselection = False)
                    entry1.delete(0, "end")
                    entry1.insert(0, '1')
                    entry1.grid(row = i, column = 1)
                    
                    tip1 = tk.Label(self, text = ' × 10 ^')
                    tip1.grid(row = i, column = 2)
                    
                    entry2 = tk.Entry(self, exportselection = False)
                    entry2.delete(0, "end")
                    entry2.insert(0, '0')
                    entry2.grid(row = i, column = 3)
                    
                    tip2 = tk.Label(self, text = ' ± ')
                    tip2.grid(row = i, column = 4)
                    
                    entry3 = tk.Entry(self, exportselection = False)
                    entry3.delete(0, "end")
                    entry3.insert(0, '1')
                    entry3.grid(row = i, column = 5)
                    
                    tip3 = tk.Label(self, text = ' × 10 ^')
                    tip3.grid(row = i, column = 6)
                    
                    entry4 = tk.Entry(self, exportselection = False)
                    entry4.delete(0, "end")
                    entry4.insert(0, '0')
                    entry4.grid(row = i, column = 7)
                    
                    self.get_value.append((entry1.get, entry2.get, entry3.get, entry4.get))
        
        class FormulaInput(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                tips = tk.Label(self, text = 'f(a, b, c, d, e) = ')
                tips.grid(row = 0, column = 0)
                
                entry = tk.Entry(self, exportselection = False, width = 81)
                entry.delete(0, "end")
                entry.insert(0, 'sqrt(exp(b ** 2)/a)')
                entry.grid(row = 0, column = 1)
                self.get_formula = entry.get
        
        class WorkPlace(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                master.value_input = ValueInput(self)
                master.value_input.grid(row = 1, column = 0)
                
                master.formula_input = FormulaInput(self)
                master.formula_input.grid(row = 0, column = 0)
                
                master.answer = tk.Text(self, undo = True, autoseparators = False)
                master.answer.grid(row = 2, column = 0)
        work_place = WorkPlace(self)
        work_place.grid(row = 1, column = 1)
        
        class StartButton(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                btn = tk.Button(self, text = '开始计算', command = master.calc)
                btn.grid(row = 0, column = 0)
        start_button = StartButton(self)
        start_button.grid(row = 0, column = 1)
    
    def calc(self):
        try:
            self.answer.delete(1.0, 'end')
            fmu = self.formula_input.get_formula().strip()
            
            def value_process():
                class Num:
                    def __init__(self, r, p, f = 1):
                        if float(r) >= 0:
                            self.f, self.r = f, r
                        else:
                            self.f, self.r = -f, r[1:]
                        if len(self.r) == 1:
                            self.r += '.'
                        self.p = int(p)
                    def __add__(self, x):
                        if type(x) == Num:
                            r = (self.f * float(self.r) * (10 ** self.p)) + (self.f * float(x.r) * (10 ** x.p))
                            l = max(self.p - len(self.r), x.p - len(x.r)) + 2
                            if r >= 0:
                                f = 1
                            else:
                                f, r = -1, -r
                            p = math.floor(math.log10(r)) if r != 0 else 0
                            r /= 10 ** (p + 1)
                            r = round(r, p - l + 1) if p + 1 >= l else 0
                            if r < 1:
                                r *= 10
                            else:
                                p -= 1
                            r = f'%.{p - l}f'%r if r != 0 else '0'
                            return Num(r, p, f)
                        else:
                            r = x
                            if r >= 0:
                                f = 1
                            else:
                                f, r= -1, -r
                            l = len(str(r)) - 2
                            l = max(l, 10)
                            p = math.floor(math.log10(r)) if r != 0 else 0
                            r /= 10 ** p
                            r = round(r, l)
                            r = f'%.{l}f'%r
                            return self.__add__(Num(r, p, f))
                    def __neg__(self):
                        return Num(self.r, self.p, -self.f)
                    def __sub__(self, x):
                        if type(x) == Num:
                            return self.__add__(self.__neg__(x))
                        else:
                            return self.__add__(-x)
                    def __mul__(self, x):
                        if type(x) == Num:
                            f = self.f * x.f
                            r = float(self.r) * float(x.r)
                            l = self.r if len(self.r) < len(x.r) else x.r
                            l = len(l) - 2 if l[0] != '8' and l[0] != '9' else len(l) - 1
                            p = math.floor(math.log10(r)) if r != 0 else 0
                            r /= 10 ** p
                            p += self.p + x.p
                            r = round(r, l)
                            r = f'%.{l}f'%r
                            print('*', self.r, x.r, r, l, p)
                            return Num(r, p, f)
                        else:
                            r = x
                            if r >= 0:
                                f = 1
                            else:
                                f, r= -1, -r
                            l = len(str(r)) - 2
                            l = max(l, 10)
                            p = math.floor(math.log10(r)) if r != 0 else 0
                            r /= 10 ** p
                            r = round(r, l)
                            r = f'%.{l}f'%r
                            return self.__mul__(Num(r, p, f))
                    def __truediv__(self, x):
                        if type(x) == Num:
                            f = self.f * x.f
                            r = float(self.r) / float(x.r)
                            l = self.r if len(self.r) < len(x.r) else x.r
                            l = len(l) - 2 if l[0] != '8' and l[0] != '9' else len(l) - 1
                            p = math.floor(math.log10(r)) if r != 0 else 0
                            r /= 10 ** p
                            p += self.p - x.p
                            r = round(r, l)
                            r = f'%.{l}f'%r
                            print('/', self.r, x.r, r, l, p)
                            return Num(r, p, f)
                        else:
                            r = x
                            if r >= 0:
                                f = 1
                            else:
                                f, r= -1, -r
                            l = len(str(r)) - 2
                            l = max(l, 10)
                            p = math.floor(math.log10(r)) if r != 0 else 0
                            r /= 10 ** p
                            r = round(r, l)
                            r = f'%.{l}f'%r
                            return self.__truediv__(Num(r, p, f))
                    def __pow__(self, x):
                        r = (self.f * float(self.r) * (10 ** self.p)) ** x
                        if r >= 0:
                            f = 1
                        else:
                            f, r= -1, -r
                        l = len(self.r) - 2
                        p = math.floor(math.log10(r)) if r != 0 else 0
                        r /= 10 ** p
                        r = round(r, l)
                        r = f'%.{l}f'%r
                        return Num(r, p, f)
                    def __radd__(self, x):
                        return self.__add__(x)
                    def __rsub__(self, x):
                        return self.__neg__(self).__add__(x)
                    def __rmul__(self, x):
                        return self.__mul__(x)
                    def __rtruediv__(self, x):
                        if type(x) == Num:
                            return x.__div__(self)
                        else:
                            r = x
                            if r >= 0:
                                f = 1
                            else:
                                f, r= -1, -r
                            l = len(str(r)) - 2
                            l = max(l, 10)
                            p = math.floor(math.log10(r)) if r != 0 else 0
                            r /= 10 ** p
                            r = round(r, l)
                            r = f'%.{l}f'%r
                            return Num(r, p, f).__truediv__(self)
                    def __rpow__(self, x):
                        r = x ** (self.f * float(self.r) * (10 ** self.p))
                        if r >= 0:
                            f = 1
                        else:
                            f, r= -1, -r
                        l = len(self.r) - 2
                        p = math.floor(math.log10(r)) if r != 0 else 0
                        r /= 10 ** p
                        r = round(r, l)
                        r = f'%.{l}f'%r
                        return Num(r, p, f)
                def abs(x):
                    if type(x) == Num:
                        return Num(x.r, x.p, 1)
                    else:
                        return x if x >= 0 else -x
                def sqrt(x):
                    return x ** 0.5
                def basefun(x, orifun):
                    if type(x) == Num:
                        r = orifun(x.f * float(x.r) * (10 ** x.p))
                        if r >= 0:
                            f = 1
                        else:
                            f, r= -1, -r
                        l = len(x.r) - 2
                        p = math.floor(math.log10(r)) if r != 0 else 0
                        r /= 10 ** p
                        r = round(r, l)
                        r = f'%.{l}f'%r
                        return Num(r, p, f)
                    else:
                        return orifun(x)
                exp = lambda x: basefun(x, math.exp)
                ln = lambda x: basefun(x, math.log)
                lg = lambda x: basefun(x, math.log10)
                sin = lambda x: basefun(x, math.sin)
                cos = lambda x: basefun(x, math.cos)
                tan = lambda x: basefun(x, math.tan)
                asin = lambda x: basefun(x, math.asin)
                acos = lambda x: basefun(x, math.acos)
                atan = lambda x: basefun(x, math.atan)
                a = Num(self.value_input.get_value[0][0](), self.value_input.get_value[0][1]())
                b = Num(self.value_input.get_value[1][0](), self.value_input.get_value[1][1]())
                c = Num(self.value_input.get_value[2][0](), self.value_input.get_value[2][1]())
                d = Num(self.value_input.get_value[3][0](), self.value_input.get_value[3][1]())
                e = Num(self.value_input.get_value[4][0](), self.value_input.get_value[4][1]())
                return eval(fmu)
            res = value_process()
            
            def error_process():
                def basefun(x, newfun, orifun):
                    if type(x) == torch.Tensor:
                        return newfun(x)
                    else:
                        return orifun(x)
                sqrt = lambda x: basefun(x, torch.sqrt, math.sqrt)
                exp = lambda x: basefun(x, torch.sqrt, math.exp)
                ln = lambda x: basefun(x, torch.sqrt, math.log)
                lg = lambda x: basefun(x, torch.sqrt, math.log10)
                sin = lambda x: basefun(x, torch.sqrt, math.sin)
                cos = lambda x: basefun(x, torch.sqrt, math.cos)
                tan = lambda x: basefun(x, torch.sqrt, math.tan)
                asin = lambda x: basefun(x, torch.sqrt, math.asin)
                acos = lambda x: basefun(x, torch.sqrt, math.acos)
                atan = lambda x: basefun(x, torch.sqrt, math.atan)
                a = torch.tensor(float(self.value_input.get_value[0][0]()) * (10 ** float(self.value_input.get_value[0][1]())), requires_grad = True)
                b = torch.tensor(float(self.value_input.get_value[1][0]()) * (10 ** float(self.value_input.get_value[1][1]())), requires_grad = True)
                c = torch.tensor(float(self.value_input.get_value[2][0]()) * (10 ** float(self.value_input.get_value[2][1]())), requires_grad = True)
                d = torch.tensor(float(self.value_input.get_value[3][0]()) * (10 ** float(self.value_input.get_value[3][1]())), requires_grad = True)
                e = torch.tensor(float(self.value_input.get_value[4][0]()) * (10 ** float(self.value_input.get_value[4][1]())), requires_grad = True)
                f = eval(fmu)
                f.backward()
                def getval(x):
                    if type(x) == torch.Tensor:
                        return x.item()
                    else:
                        return 0
                u = math.sqrt(((getval(a.grad) * float(self.value_input.get_value[0][2]()) * (10 ** float(self.value_input.get_value[0][3]()))) ** 2) +
                              ((getval(b.grad) * float(self.value_input.get_value[1][2]()) * (10 ** float(self.value_input.get_value[1][3]()))) ** 2) +
                              ((getval(c.grad) * float(self.value_input.get_value[2][2]()) * (10 ** float(self.value_input.get_value[2][3]()))) ** 2) +
                              ((getval(d.grad) * float(self.value_input.get_value[3][2]()) * (10 ** float(self.value_input.get_value[3][3]()))) ** 2) +
                              ((getval(e.grad) * float(self.value_input.get_value[4][2]()) * (10 ** float(self.value_input.get_value[4][3]()))) ** 2) )
                v = float('%.1g'%u)
                u = v if v > u else float('%.1g'%(v + 10 ** math.floor(math.log10(v))))
                return u
            u = error_process()
            
            r = res.f * float(res.r) * (10 ** res.p)
            r = round(r, -math.floor(math.log10(u)))
            self.answer.insert('insert', f'计算结果为{r}±{u}')
        except:
            messagebox.showerror(title = '错误', message = '计算过程出现问题，请检查输入是否有误！')

class LineGenerate(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        self.title = tk.Label(self, text = '使用最小二乘法拟合直线并绘图')
        self.title.grid(row = 0, column = 0)
        
        class ValueInput(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                tip = tk.Label(self, text = 'x = ')
                tip.grid(row = 0, column = 0)
                tip = tk.Label(self, text = 'y = ')
                tip.grid(row = 0, column = 1)
        
                self.get_value = []
                for i in range(10):
                    entry1 = tk.Entry(self, exportselection = False)
                    entry1.delete(0, "end")
                    entry1.grid(row = i + 2, column = 0)
                    entry2 = tk.Entry(self, exportselection = False)
                    entry2.delete(0, "end")
                    entry2.grid(row = i + 2, column = 1)
                    self.get_value.append((entry1.get, entry2.get))
        self.value_input = ValueInput(self)
        self.value_input.grid(row = 1, column = 0)
        
        class DrawPic(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                self.answer = tk.Entry(self, exportselection = False, width = 81)
                self.answer.delete(0, "end")
                self.answer.grid(row = 0, column = 0)
                
                self.photo = tk.Label(self, bg = '#FFFFFF', height = 25, width = 81)
                self.photo.grid(row = 1, column = 0)
        self.draw_pic = DrawPic(self)
        self.draw_pic.grid(row = 1, column = 1)
        
        class StartSaveButton(tk.Frame):
            def __init__(self, master):
                super().__init__(master)
                
                btn = tk.Button(self, text = '开始计算', command = master.calc)
                btn.grid(row = 0, column = 0)
                
                btn1 = tk.Button(self, text = '保存图片', command = master.asksave)
                btn1.grid(row = 0, column = 1)
        
        start_save_button = StartSaveButton(self)
        start_save_button.grid(row = 0, column = 1)
    
    def calc(self):
        try:
            x, y = [], []
            for i in range(10):
                try:
                    tmp_x, tmp_y = float(self.value_input.get_value[i][0]().strip()), float(self.value_input.get_value[i][1]().strip())
                except:
                    break
                x.append(tmp_x)
                y.append(tmp_y)
            n = len(x)
            ax = ay = axx = ayy = axy = 0
            for i in range(n):
                ax += x[i]
                ay += y[i]
                axx += x[i] * x[i]
                ayy += y[i] * y[i]
                axy += x[i] * y[i]
            ax /= n
            ay /= n 
            axx /= n
            ayy /= n 
            axy /= n
            r = (axy - ax * ay) / math.sqrt((axx - ax * ax) * (ayy - ay * ay))
            a = (axy - ax * ay) / (axx - ax * ax)
            b = ay - a * ax
            
            self.draw_pic.answer.delete(0, "end")
            self.draw_pic.answer.insert(0, f'y = {a}x + {b}, R = {r}')
            
            xl = np.linspace(min(x), max(x), 50)
            yl = a * xl + b
            fig = plt.figure()
            plt.plot(xl, yl)
            plt.scatter(x, y)
            buf = io.BytesIO()
            fig.canvas.print_png(buf)
            data = buf.getvalue()
            buf.write(data)
            self.img = Image.open(buf)
            self.photo = ImageTk.PhotoImage(self.img)
            self.draw_pic.photo.destroy()
            self.draw_pic.photo = tk.Label(self.draw_pic, image = self.photo)
            self.draw_pic.photo.grid(row = 1, column = 0)
        except:
            messagebox.showerror(title = '错误', message = '计算过程出现问题，请检查输入是否有误！')
    def asksave(self):
        try:
            filetypes = [("PNG", "*.png"), ("JPG", "*.jpg"), ("txt files", "*.txt"), ('All files', '*')]
            filename = asksaveasfilename(title = '保存图片',
                                        filetypes = filetypes,
                                        defaultextension = '.png',
                                        initialdir = '.')
            self.img.save(filename)
            messagebox.showinfo(title = '成功', message = '保存成功')
        except:
            messagebox.showerror(title = '错误', message = '保存失败')


class ChooseFunction(tk.Frame):
    def __init__(self, master, callback):
        super().__init__(master)
        FUNCTIONS = ['测量数据处理', '间接测量计算', '拟合直线']
        self.v = tk.IntVar()
        for i in range(len(FUNCTIONS)):
            radio_button = tk.Radiobutton(self, text = FUNCTIONS[i], variable = self.v, value = i, command = lambda: callback(self.v.get()), indicatoron = False)
            radio_button.grid(row = 0, column = i)

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PhysicsDataProcess - v0.1.0')
        self.iconbitmap(os.path.abspath(__file__ + '/../resources/logo.ico'))
        
        measure_process = MeasureProcess(self)
        data_calculate = DataCalculate(self)
        line_generate = LineGenerate(self)
        def choose_fun(x):
            FUNCTIONS = [measure_process, data_calculate, line_generate]
            for fun in FUNCTIONS:
                if fun:
                    fun.pack_forget()
            if FUNCTIONS[x]:
                FUNCTIONS[x].pack()
        choose_function = ChooseFunction(self, choose_fun)
        
        choose_function.pack(anchor = 'w')
        measure_process.pack()
        
        def _quit():
            self.quit()
            self.destroy() 
        self.protocol("WM_DELETE_WINDOW", _quit)
        self.mainloop()

if __name__ == '__main__':
    torch.device('cpu')
    MainWindow()