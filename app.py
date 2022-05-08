import tkinter as tk
from functools import partial
from turtle import update

DIR = [ # [y, x]
    [-1, 0], # upper
    [-1, 1], # upper_right
    [ 0, 1], # right
    [ 1, 1], # lower_right
    [ 1, 0], # lower
    [ 1,-1], # lower_left
    [ 0,-1], # left
    [-1,-1], # upper_left
]
EMPTY = 0

class application(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self,root)
        self.play_num = 18
        self.size = int((self.play_num / 2) ** 0.5) * 8
        self.colors = ['black', 'white', 'red', 'blue', 'cyan', 'yellow', 'magenta', 'lime green', 'aquamarine', 'purple', 'dark olive green', 'navy', 'maroon', 'gray', 'peach puff', 'cadet blue', 'khaki', 'orange']
        self.turns = 0
        self.current_num = 0
        self.is_end = False
        # 各プレイヤーが打てるか
        self.can_put = [True] * self.play_num
        
        self.maxturn = self.size * self.size - self.play_num * 2
        
        self.createboard()
        self.createinfo()
        # 打てる座標リストの初期化
        print("create")
        self.init_cml()
        
        
        
    def move(self, y, x):
        print(y,x)
        print(self.cml)
        if not (y, x) in self.cml:
            return False
        dirs = self.cmil[self.cml.index((y, x))]
        self.reverse(y, x, dirs)
        self.turns += 1
        self.current_num = (self.current_num + 1) % self.play_num
        
        self.init_cml()
        
        # 置けるところがない && ゲームオーバーでない間スキップする
        while not self.cml and not self.isgameover():
            self.can_put[self.current_num] = False
            self.skip()

        if self.cml:
            self.can_put[self.current_num] = True
        
        self.update_info()
        return True
        
    def reverse(self, y, x, dirs):
        self.put(y, x, self.current_num)
        for dir, cnt in dirs:
            inc = DIR[dir]
            yt = y + inc[0]
            xt = x + inc[1]
            for _ in range(cnt):
                self.flip(yt, xt, self.current_num)
                yt += inc[0]
                xt += inc[1]
        
    # 石のおける場所とひっくり返る方向、枚数を更新
    def init_cml(self):
        cml = []
        cmil = []
        for i in range(self.size):
            for j in range(self.size):
                cm = self.can_move(i, j)
                if cm:
                    cml.append((i, j))
                    cmil.append(cm)
        self.cml = tuple(cml)
        self.cmil = tuple(cmil)
        
    # return ((DIR_num, cnt),・・・)
    def can_move(self, y, x):
        movable = []
        num = self.current_num
        if not self.is_empty(y, x):
            return ()
        for i, d in enumerate(DIR):
            yt = y + d[0]
            xt = x + d[1]
            if not self.within(yt, xt):
                continue
            if self.is_empty(yt, xt):
                continue
            if self.is_same_color(yt, xt, self.colors[num]):
                continue
            cnt = 1
            yt += d[0]
            xt += d[1]
            while self.within(yt, xt) and not self.is_empty(yt, xt):
                if self.is_same_color(yt, xt, self.colors[num]):
                    movable.append((i, cnt))
                    break
                cnt += 1
                yt += d[0]
                xt += d[1]
        return tuple(movable)
    
    # 指定のマスが、指定の色のマスか
    def is_same_color(self, y, x, color):
        return self.squares[y][x]["foreground"] == color
    
    # 指定のマスが空の状態か
    def is_empty(self, y, x):
        return self.is_same_color(y, x, "SystemButtonText")
        
    # 範囲内か
    def within(self, y, x):
        return 0 <= y < self.size and 0 <= x < self.size
    
    # 置けない場合のスキップ処理
    def skip(self):
        # 置ける or すでにゲーム終了している
        if self.cml or self.is_end:
            return False
        
        self.current_num = (self.current_num + 1) % self.play_num
        self.init_cml()
        return True
    
    def isgameover(self):
        if self.is_end:
            return True
        if self.turns >= self.maxturn:
            self.is_end = True
            return True
        if not any(self.can_put):
            self.is_end = True
            return True
        return False
        
    def createboard(self):
        self.board = tk.Frame(self)
        self.board.pack(side=tk.LEFT)

        self.frames = []
        self.squares = []
        kw = {
            #"image": tk.PhotoImage(),
            "bg": "green",
            #"compound": "center",
            #"text": " ",
            #"height": 1,
            #"width": 1,
            "font": ("",48),
            "activebackground": "green"
        }
        for i in range(self.size):
            self.frames.append([])
            self.squares.append([])
            for j in range(self.size):
                """
                ボタンを格納するフレームを作成
                tk.Frame().propagate(False)で、中身の大きさに左右されず、フレームのsizeを反映することができる。
                buttonはpixelでのサイズ指定ができないため、このようにする必要がある。
                """
                self.frames[i].append(tk.Frame(self.board, width = 38, height = 38))
                self.frames[i][j].propagate(False)
                self.frames[i][j].grid(row=i,column=j,sticky = "nsew")
                
                kw["command"] = partial(self.move, i, j)
                #kw["command"] = lambda: self.move(i,j)
                self.squares[i].append(tk.Button(self.frames[i][j],**kw))
                # expandはTrueとした時、残っている領域全てを占有領域とする
                # fillは占有領域に対して、ウィジェットの幅、高さ、もしくは両方を合わせる
                self.squares[i][j].pack(expand=True, fill=tk.BOTH)
                
                
        # 初期配置
        pnum = 0
        
        for i in range(3, self.size, 8):
            for j in range(3, self.size, 8):
                self.put(i, j, pnum)
                self.put(i+1, j+1, pnum)
                pnum += 1
                self.put(i+1, j, pnum)
                self.put(i, j+1, pnum)
                pnum += 1
    
    def createinfo(self):
        tmp = {
            "bg": "green"
        }
        char = {
            "font": ("",24),
            "foreground":"white"
        }
        self.info = tk.Frame(self, width = 300, height = 912, **tmp, relief=tk.RAISED, bd=10)
        self.info.propagate(False)
        self.info.pack(side=tk.LEFT)
        
        self.info_turn = tk.Frame(self.info, **tmp)
        self.info_turn.pack()
        self.tcframe = tk.Frame(self.info_turn, width=38,height=38)
        self.tcframe.propagate(False)
        self.tcframe.pack(side=tk.LEFT)
        self.tcolor = tk.Label(self.tcframe, text="●", font=("",48), **tmp, relief=tk.RAISED, bd=2, fg=self.colors[self.current_num])
        self.tcolor.pack()
        self.ttext = tk.Label(self.info_turn, text="のターン", **tmp, **char)
        self.ttext.pack(side=tk.LEFT)
        
    def update_info(self):
        if self.is_end:
            self.tcframe.pack_forget()
            self.ttext["text"] = "試合終了"
            return
        self.tcolor["fg"] = self.colors[self.current_num]
    
    def flip(self, i, j, num):
        self.squares[i][j]["fg"] = self.colors[num]
        self.squares[i][j]["disabledforeground"] = self.colors[num]
    
    def put(self, i, j, num):
        self.squares[i][j]["text"] = "●"
        #self.squares[i][j]["activebackground"] = "green"
        #self.squares[i][j]["activeforeground"] = "green"
        self.squares[i][j]["state"] = tk.DISABLED
        self.flip(i, j, num)
        
        
if __name__ == "__main__":
    root = tk.Tk()
    root.title('multiple_reversi')
    root.geometry('1212x912')
    app = application(root)
    app.pack()
    app.mainloop()

