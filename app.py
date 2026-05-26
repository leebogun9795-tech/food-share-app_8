import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import random
import os
from PIL import Image, ImageTk

class ShareFridgeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("공유냉장고 : 우리 동네 소통 플랫폼")
        self.root.geometry("1000x800")
        
        # --- 핵심 데이터 변수 ---
        self.my_location = "위치 미인증"
        self.is_authenticated = False
        self.total_carbon_saved = 0.0
        self.my_manner_temp = 36.5
        self.my_wishlist = []  
        self.my_coords = (0, 0) # 초기 좌표는 0으로 설정 (인증 시 생성)

        # 사용자별 매너 온도 데이터
        self.user_temperatures = {
            "나": 36.5,
            "신촌불주먹": 37.2,
            "노원지킴이": 36.0,
            "상계동주민": 40.5,
            "꿀팁요정": 38.0,
            "자취고수": 39.1
        }

        # 공유 냉장고 고정 위치 정보 (상계동 내 가상 좌표)
        self.fridge_locations = {
            "상계 1호점": (200, 150),
            "상계 2호점": (500, 200),
            "상계 3호점": (350, 350)
        }
        
        self.chats = {}
        self.community_posts = [
            {"id": 1, "user": "꿀팁요정", "content": "1호 공유냉장고에 오늘 신선한 채소가 많이 들어왔네요!", "time": "10분 전"},
            {"id": 2, "user": "자취고수", "content": "역 앞 마트 오늘 타임세일 한대요. 참고하세요~", "time": "30분 전"}
        ]
        
        self.foods = [
            {
                "id": 1, "name": "감자 3알", "type": "무료나눔", 
                "exp_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), 
                "user": "신촌불주먹", "carbon": 0.3, "status": "실온", 
                "fridge": "상계 1호점",
                "desc": "요리하고 남았어요.", "cook_date": "2026-05-13", "storage": "서늘한 곳 보관"
            },
            {
                "id": 2, "name": "우유 500ml (미개봉)", "type": "무료나눔", 
                "exp_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"), 
                "user": "노원지킴이", "carbon": 0.5, "status": "냉장", 
                "fridge": "상계 2호점",
                "desc": "유통기한 임박해서 나눔합니다.", "cook_date": "안 했어요.", "storage": "냉장 보관"
            },
            {
                "id": 3, "name": "방울토마토 한 팩", "type": "물물교환", 
                "exp_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"), 
                "user": "상계동주민", "carbon": 0.4, "status": "냉장", 
                "fridge": "상계 3호점",
                "desc": "사과나 다른 과일이랑 바꾸고 싶어요!", "cook_date": "2026-05-14", "storage": "냉장 보관"
            }
        ]
        
        self.setup_ui()

    def setup_ui(self):
        # 헤더 영역
        self.header = tk.Frame(self.root, bg="#c6e6a1", pady=10)
        self.header.pack(fill="x")
        
        self.loc_label = tk.Label(self.header, text=f"📍 {self.my_location}", bg="#747474", fg="white", font=("Arial", 10, "bold"))
        self.loc_label.pack(side="left", padx=15)
        
        self.auth_btn = tk.Button(self.header, text="동네 인증하기", command=self.authenticate_location, bg="#4caf50", fg="white", font=("Arial", 8))
        self.auth_btn.pack(side="left")
        
        self.carbon_label = tk.Label(self.header, text=f"🌱 탄소 절감: {self.total_carbon_saved:.2f}kg", bg="#f1f8e9", fg="#2E7D32")
        self.carbon_label.pack(side="left", padx=20)
        
        self.manner_label = tk.Label(self.header, text=f"🌡️ 매너 온도: {self.my_manner_temp:.1f}℃", bg="#f1f8e9", fg="#FF5722")
        self.manner_label.pack(side="right", padx=15)

        # 탭 메뉴 영역
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_list = tk.Frame(self.tabs)
        self.tab_chat_list = tk.Frame(self.tabs) 
        self.tab_community = tk.Frame(self.tabs)
        self.tab_map = tk.Frame(self.tabs)
        self.tab_reg = tk.Frame(self.tabs)
        self.tab_settings = tk.Frame(self.tabs)

        self.tabs.add(self.tab_list, text=" 🍲 음식 공유 ")
        self.tabs.add(self.tab_chat_list, text=" 💬 채팅목록 ") 
        self.tabs.add(self.tab_community, text=" 🏡 동네생활 ")
        self.tabs.add(self.tab_map, text=" 📍 지도 ")
        self.tabs.add(self.tab_reg, text=" ✍️ 나눔하기 ")
        self.tabs.add(self.tab_settings, text=" ⚙️ 설정 ")

        # 초기 화면 그리기
        self.draw_list()
        self.draw_chat_list() 
        self.draw_community()
        self.draw_map()
        self.draw_registration()
        self.draw_settings()

    def authenticate_location(self):
        loc_list = ["서울시 노원구 상계동"]
        detected = random.choice(loc_list)
        
        if messagebox.askyesno("위치 감지", f"현재 위치가 '{detected}' 맞나요?\n동네 인증을 완료합니다."):
            self.my_location = detected
            self.is_authenticated = True
            
            # 지도 위에 겹치지 않게 가상의 내 위치 좌표 배정 (지도 캔버스 크기 고려)
            self.my_coords = (random.randint(250, 650), random.randint(250, 550))
            
            self.loc_label.config(
                text=f"✅ {self.my_location}", 
                bg="#41CA65", 
                fg="black"
            )
            self.auth_btn.config(state="disabled", text="인증 완료")

            # 인증이 필요한 탭 실시간 새로고침
            self.draw_community() 
            self.draw_map()
            messagebox.showinfo("성공", f"{detected} 커뮤니티에 입장하셨습니다!")

    def draw_chat_list(self):
        for widget in self.tab_chat_list.winfo_children(): widget.destroy()
        tk.Label(self.tab_chat_list, text="진행 중인 채팅", font=("Arial", 12, "bold")).pack(pady=10)
        
        if not self.chats:
            tk.Label(self.tab_chat_list, text="진행 중인 채팅이 없습니다.", fg="gray").pack(pady=50)
            return
            
        for food_id, chat_data in self.chats.items():
            food = chat_data["food"]
            unread = chat_data["unread"]
            card = tk.Frame(self.tab_chat_list, relief="groove", bd=1, pady=10, padx=15)
            card.pack(fill="x", padx=20, pady=5)
            
            title_text = f"👤 {food['user']} ({food['name']})"
            lbl = tk.Label(card, text=title_text, font=("Arial", 10, "bold"))
            lbl.pack(side="left")
            
            if unread > 0:
                tk.Label(card, text=f" {unread} ", bg="red", fg="white", font=("Arial", 8, "bold")).pack(side="left", padx=5)
            
            last_msg = chat_data["messages"][-1]["text"] if chat_data["messages"] else "대화를 시작해보세요."
            tk.Label(card, text=f"|  {last_msg[:20]}...", fg="gray").pack(side="left", padx=10)
            tk.Button(card, text="열기", command=lambda f=food: self.open_chat(f)).pack(side="right")

    def draw_list(self):
        for widget in self.tab_list.winfo_children(): widget.destroy()
        canvas = tk.Canvas(self.tab_list)
        scroll = ttk.Scrollbar(self.tab_list, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        
        for food in self.foods:
            card = tk.Frame(frame, relief="groove", bd=1, pady=10, padx=10, width=700)
            card.pack(fill="x", padx=20, pady=5)
            
            title_frame = tk.Frame(card)
            title_frame.pack(fill="x")
            
            tk.Label(title_frame, text=f"[{food['status']}] {food['name']}", font=("Arial", 11, "bold"), fg="#2E7D32").pack(side="left")
            tk.Label(title_frame, text=f"📍 {food['fridge']}", font=("Arial", 9), fg="#1976D2").pack(side="left", padx=10)
            
            user_name = food['user']
            profile_btn = tk.Button(title_frame, text=f"👤 {user_name}", font=("Arial", 9, "underline"), 
                                    fg="#555", cursor="hand2", relief="flat", padx=5,
                                    command=lambda u=user_name: self.show_profile(u))
            profile_btn.pack(side="right")
            
            if food['user'] == "나":
                tk.Label(card, text="내 게시글", font=("Arial", 9, "italic"), fg="gray", padx=10).pack(side="right")
            else:
                tk.Button(card, text="채팅하기", command=lambda f=food: self.open_chat(f), bg="#e8f5e9").pack(side="right")
            
            info_text = f"방식: {food['type']} | 기한: {food['exp_date']} | 보관: {food.get('storage', '-')} | 조리: {food.get('cook_date', '-')}"
            tk.Label(card, text=info_text, fg="gray", justify="left").pack(anchor="w", padx=5)
            
        canvas.configure(yscrollcommand=scroll.set)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def show_profile(self, username):
        """사용자 프로필 팝업 창 상세 구현"""
        profile_win = tk.Toplevel(self.root)
        profile_win.title(f"{username}님의 프로필")
        profile_win.geometry("400x520")
        profile_win.configure(bg="white")
        profile_win.resizable(False, False)

        # 상단 헤더 영역
        header = tk.Frame(profile_win, bg="#f4fbf0", pady=20)
        header.pack(fill="x")
        
        temp = self.user_temperatures.get(username, 36.5)
        
        tk.Label(header, text=f"👤 {username}", font=("Arial", 16, "bold"), bg="#f4fbf0").pack()
        tk.Label(header, text=f"🌡️ 매너 온도: {temp:.1f}℃", font=("Arial", 12, "bold"), fg="#FF5722", bg="#f4fbf0").pack(pady=5)
        
        # [추가] 최근 접속 시간 데이터 분기 처리
        active_time = "방금 전" if username == "나" else f"{random.randint(1, 55)}분 전"
        tk.Label(header, text=f"⏱️ 최근 접속: {active_time}", font=("Arial", 9), fg="gray", bg="#f4fbf0").pack()

        # 주요 콘텐츠 프레임
        content = tk.Frame(profile_win, bg="white", padx=20, pady=10)
        content.pack(fill="both", expand=True)

        # 1. 작성한 나눔 글 목록 섹션
        tk.Label(content, text="📋 올린 제품 목록", font=("Arial", 11, "bold"), bg="white", fg="#2E7D32").pack(anchor="w", pady=(15, 5))
        user_items = [f for f in self.foods if f['user'] == username]
        
        if user_items:
            for item in user_items:
                item_frame = tk.Frame(content, bg="white")
                item_frame.pack(anchor="w", fill="x", padx=10, pady=2)
                tk.Label(item_frame, text=f"• {item['name']}", bg="white", fg="#444", font=("Arial", 10)).pack(side="left")
                tk.Label(item_frame, text=f"({item['fridge']})", bg="white", fg="gray", font=("Arial", 8)).pack(side="left", padx=5)
        else:
            tk.Label(content, text="등록된 제품이 없습니다.", bg="white", fg="gray", font=("Arial", 10, "italic")).pack(anchor="w", padx=10)

        # 2. 최근 거래 내역 섹션
        tk.Label(content, text="🤝 최근 동네 거래 내역", font=("Arial", 11, "bold"), bg="white", fg="#1976D2").pack(anchor="w", pady=(25, 5))
        
        trades = ["딸기 나눔 완료", "신선 우유 교환 완료", "모닝빵 나눔 완료"] if username != "나" else ["아직 완료된 거래 내역이 없습니다."]
        for t in trades:
            tk.Label(content, text=f"✓ {t}", bg="white", fg="#555", font=("Arial", 10)).pack(anchor="w", padx=10, pady=2)

        # 하단 닫기 버튼
        tk.Button(profile_win, text="창 닫기", command=profile_win.destroy, width=12, bg="#f5f5f5", relief="groove").pack(pady=15)

    def open_chat(self, food):
        fid = food['id']
        if fid not in self.chats:
            self.chats[fid] = {"food": food, "messages": [], "unread": 0}
        
        self.chats[fid]["unread"] = 0 
        self.draw_chat_list()
        
        win = tk.Toplevel(self.root)
        win.title(f"{food['user']}님과의 채팅")
        win.geometry("400x550")
        
        display = tk.Text(win, bg="#fefefe", state="disabled", height=15)
        display.pack(fill="both", expand=True, padx=10, pady=10)
        
        def update_display():
            display.config(state="normal")
            display.delete("1.0", "end")
            display.insert("end", f"[시스템] : '{food['name']}' 거래 채팅방입니다.\n\n")
            for m in self.chats[fid]["messages"]:
                display.insert("end", f"[{m['sender']}] : {m['text']}\n")
            display.config(state="disabled")
            display.see("end")

        update_display()
        
        input_f = tk.Frame(win)
        input_f.pack(fill="x", padx=10)
        ent = tk.Entry(input_f)
        ent.pack(side="left", fill="x", expand=True, padx=5)
        
        def receive_msg(sender, text):
            self.chats[fid]["messages"].append({"sender": sender, "text": text})
            if win.winfo_exists():
                update_display()
            else:
                self.chats[fid]["unread"] += 1
            self.draw_chat_list()

        def send():
            msg = ent.get()
            if not msg: return
            receive_msg("나", msg)
            ent.delete(0, "end")
            
            if "안녕하세요" in msg:
                response = "안녕하세요! 거래 가능합니다."
            else:
                responses = ["지금 바로 갈 수 있어요!", "감사합니다!", "어디서 뵐까요?", "좋은 나눔 감사합니다!"]
                response = random.choice(responses)
            win.after(800, lambda: receive_msg(food['user'], response))

        tk.Button(input_f, text="전송", command=send, bg="#4caf50", fg="white").pack(side="right")

        def complete_trade():
            if messagebox.askyesno("거래 확인", "거래가 잘 이루어졌나요?"):
                eval_win = tk.Toplevel(win)
                eval_win.title("매너 평가")
                eval_win.geometry("300x180")
                
                target_user = food['user']
                tk.Label(eval_win, text=f"'{target_user}'님과의 거래는 어떠셨나요?\n매너 온도를 평가해주세요.", pady=15).pack()
                
                def update_temp(delta):
                    if target_user in self.user_temperatures:
                        self.user_temperatures[target_user] += delta
                        self.user_temperatures[target_user] = max(0, min(99, round(self.user_temperatures[target_user], 1)))
                    
                    self.manner_label.config(text=f"🌡️ 매너 온도: {self.user_temperatures['나']:.1f}℃")
                    
                    eval_win.destroy()
                    win.destroy()
                    messagebox.showinfo("평가 완료", f"'{target_user}'님의 온도가 {delta:+.1f}℃ 반영되었습니다!\n현재 온도: {self.user_temperatures[target_user]:.1f}℃")

                btn_frame = tk.Frame(eval_win)
                btn_frame.pack(pady=10)
                tk.Button(btn_frame, text="👍 최고예요 (+0.1)", bg="#4caf50", fg="white", width=15,
                          command=lambda: update_temp(0.1)).pack(pady=2)
                tk.Button(btn_frame, text="👎 별로예요 (-0.1)", bg="#f44336", fg="white", width=15,
                          command=lambda: update_temp(-0.1)).pack(pady=2)

        tk.Button(win, text="🤝 거래 완료 및 평가하기", command=complete_trade, bg="#FF9800", fg="white", pady=5).pack(fill="x", padx=10, pady=10)

    def draw_community(self):
        for widget in self.tab_community.winfo_children(): widget.destroy()
        
        # [가드 로직 적용] 미인증 유저는 동네생활 열람 불가하게 처리
        if not self.is_authenticated:
            info_frame = tk.Frame(self.tab_community)
            info_frame.place(relx=0.5, rely=0.5, anchor="center")
            tk.Label(info_frame, text="🔒", font=("Arial", 40)).pack()
            tk.Label(info_frame, text="동네 인증을 완료해야 글을 열람하고 작성할 수 있습니다.", font=("Arial", 12, "bold"), fg="gray").pack(pady=10)
            return

        tk.Label(self.tab_community, text="🏡 우리 동네 실시간 정보통", font=("Arial", 12, "bold")).pack(pady=10)
        
        post_frame = tk.Frame(self.tab_community, pady=10)
        post_frame.pack(fill="x", padx=20)
        post_ent = tk.Entry(post_frame)
        post_ent.pack(side="left", fill="x", expand=True, padx=5)
        
        def add_post():
            content = post_ent.get()
            if content:
                self.community_posts.insert(0, {
                    "id": len(self.community_posts)+1, 
                    "user": "나", "content": content, "time": "방금 전"
                })
                post_ent.delete(0, "end")
                self.draw_community()
        
        tk.Button(post_frame, text="올리기", command=add_post, bg="#007bff", fg="white").pack(side="right")
        
        list_container = tk.Frame(self.tab_community)
        list_container.pack(fill="both", expand=True, padx=20, pady=5)
        canvas = tk.Canvas(list_container)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=740)
        canvas.configure(yscrollcommand=scrollbar.set)

        for post in self.community_posts:
            p_card = tk.Frame(scrollable_frame, pady=10)
            p_card.pack(fill="x")
            post_user = post['user']
            
            # 닉네임 버튼 연결 안정화
            user_btn = tk.Button(
                p_card, 
                text=f"👤 {post_user}", 
                font=("Arial", 10, "bold", "underline"), 
                fg="#333",
                bd=0, 
                bg=p_card.cget("bg"), 
                activebackground=p_card.cget("bg"),
                cursor="hand2",
                command=lambda u=post_user: self.show_profile(u)
            )
            user_btn.pack(anchor="w")

            tk.Label(p_card, text=post['content'], wraplength=700, justify="left", font=("Arial", 10)).pack(anchor="w", pady=4)
            tk.Label(p_card, text=post['time'], font=("Arial", 8), fg="gray").pack(anchor="w")
            tk.Frame(scrollable_frame, height=1, bg="#eee").pack(fill="x", pady=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def draw_map(self):
        """지도 탭을 그리는 메서드 (내 위치 마커 실시간 렌더링 반영)"""
        for widget in self.tab_map.winfo_children(): 
            widget.destroy()
        
        tk.Label(self.tab_map, text="📍 상계동 공유 냉장고 현황", font=("Arial", 12, "bold")).pack(pady=5)
        
        canvas_width = 950
        canvas_height = 650
        canvas = tk.Canvas(self.tab_map, width=canvas_width, height=canvas_height, bg="white")
        canvas.pack(pady=10)

        # 지도 이미지 배경 설정
        img_path = "KakaoTalk_20260516_030139850_01.jpg"
        
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img = img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                self.bg_img = ImageTk.PhotoImage(img)
                canvas.create_image(0, 0, anchor="nw", image=self.bg_img)
            except Exception as e:
                canvas.create_text(canvas_width//2, canvas_height//2, text=f"이미지 로드 에러: {e}", fill="red")
        else:
            canvas.config(bg="#e8f5e9")
            canvas.create_text(canvas_width//2, canvas_height//2, 
                               text=f"지도 파일({img_path})을 찾을 수 없습니다.\n배경색 모드로 대체합니다.", 
                               font=("Arial", 13, "bold"), fill="gray", justify="center")

        # --- [데이터 표시] 냉장고 아이콘 렌더링 ---
        for name, pos in self.fridge_locations.items():
            fx, fy = pos
            canvas.create_rectangle(fx-20, fy-25, fx+20, fy+25, fill="#2E7D32", outline="white", width=2)
            canvas.create_rectangle(fx-18, fy-22, fx+18, fy+5, fill="#A5D6A7")
            canvas.create_text(fx, fy-40, text=name, font=("Arial", 10, "bold"), fill="black")
            
            count = len([f for f in self.foods if f['fridge'] == name])
            canvas.create_text(fx, fy+40, text=f"음식 {count}개", font=("Arial", 9, "bold"), fill="#1B5E20")

        # --- [추가 변경분] 내 위치 마커 조건부 렌더링 ---
        if self.is_authenticated:
            mx, my = self.my_coords
            # 반경 12px 크기의 눈에 띄는 주황/빨간색 마커 생성
            canvas.create_oval(mx-12, my-12, mx+12, my+12, fill="#FF5722", outline="white", width=3)
            canvas.create_oval(mx-4, my-4, mx+4, my+4, fill="white") # 마커 중심점 강조
            
            # 마커 상단 텍스트 레이블 가독성 확보를 위한 투명 사각형 베이스
            canvas.create_text(mx, my-25, text="🙋 내 위치 (인증됨)", font=("Arial", 10, "bold"), fill="#D84315")
        else:
            # 인증 전 상태 가이드라인 출력
            canvas.create_rectangle(canvas_width//2 - 150, 20, canvas_width//2 + 150, 60, fill="#FFF9C4", outline="#FBC02D")
            canvas.create_text(canvas_width//2, 40, text="상단 [동네 인증하기] 완료 시 내 위치가 표시됩니다.", font=("Arial", 9), fill="#F57F17")

    def draw_registration(self):
        for widget in self.tab_reg.winfo_children(): widget.destroy()
        f = tk.Frame(self.tab_reg, padx=50, pady=20); f.pack()
        
        fields = [
            ("음식명:", tk.Entry),
            ("보관 냉장고:", ttk.Combobox),
            ("거래 방식:", ttk.Combobox),
            ("보관 상태:", ttk.Combobox),
            ("유통기한:", tk.Entry),
            ("조리 날짜:", tk.Entry),
            ("상세 보관방법:", tk.Entry)
        ]
        
        self.reg_inputs = {}
        for i, (label, widget_type) in enumerate(fields):
            tk.Label(f, text=label).grid(row=i, column=0, pady=5, sticky="w")
            if widget_type == ttk.Combobox:
                if "냉장고" in label:
                    w = widget_type(f, values=list(self.fridge_locations.keys()), state="readonly", width=23)
                    w.set(list(self.fridge_locations.keys())[0])
                elif "방식" in label:
                    w = widget_type(f, values=["무료나눔", "물물교환", "소액판매"], width=23)
                    w.set("무료나눔")
                else:
                    w = widget_type(f, values=["냉장", "냉동", "실온"], width=23)
                    w.set("냉장")
            else:
                w = widget_type(f, width=25)
                if "기한" in label or "날짜" in label:
                    w.insert(0, datetime.now().strftime("%Y-%m-%d"))
            w.grid(row=i, column=1, pady=5)
            self.reg_inputs[label] = w

        def register():
            name = self.reg_inputs["음식명:"].get()
            if not name:
                messagebox.showwarning("경고", "음식명을 입력해주세요.")
                return
            
            selected_fridge = self.reg_inputs["보관 냉장고:"].get()
            new_item = {
                "id": len(self.foods)+1, "name": name, 
                "type": self.reg_inputs["거래 방식:"].get(),
                "exp_date": self.reg_inputs["유통기한:"].get(),
                "status": self.reg_inputs["보관 상태:"].get(),
                "user": "나", "fridge": selected_fridge, 
                "carbon": 0.45, "storage": self.reg_inputs["상세 보관방법:"].get(),
                "cook_date": self.reg_inputs["조리 날짜:"].get()
            }
            self.foods.append(new_item)
            self.total_carbon_saved += 0.45
            self.carbon_label.config(text=f"🌱 탄소 절감: {self.total_carbon_saved:.2f}kg")
            self.draw_list(); self.draw_map(); self.tabs.select(0)
            messagebox.showinfo("등록 완료", f"'{name}'을(를) {selected_fridge}에 등록했습니다!")

        tk.Button(f, text="등록하기", bg="#2E7D32", fg="white", font=("Arial", 10, "bold"), command=register).grid(row=7, columnspan=2, pady=20)

    def draw_settings(self):
        for widget in self.tab_settings.winfo_children(): widget.destroy()
        tk.Label(self.tab_settings, text="🔔 알람 설정", font=("Arial", 12, "bold")).pack(pady=20)
        wish_frame = tk.Frame(self.tab_settings, pady=10); wish_frame.pack()
        wish_ent = tk.Entry(wish_frame); wish_ent.pack(side="left", padx=5)
        
        def add_wish():
            item = wish_ent.get()
            if item: 
                self.my_wishlist.append(item)
                self.draw_settings()
        
        tk.Button(wish_frame, text="키워드 추가", command=add_wish).pack(side="right")
        tk.Label(self.tab_settings, text=f"관심 키워드: {', '.join(self.my_wishlist)}", fg="blue").pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ShareFridgeApp(root)
    root.mainloop()
