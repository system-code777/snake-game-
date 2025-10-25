import sys
import os
import random
import pygame

# 配置
CELL_SIZE = 20
GRID_W, GRID_H = 30, 20
WIDTH, HEIGHT = CELL_SIZE * GRID_W, CELL_SIZE * GRID_H
OFFSET_X, OFFSET_Y = 0, 0  # 新增：绘制偏移以实现居中
FPS = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 150, 255)
FONT_SZ = 24

# 可配置选项（开始界面的设置）
LANG_OPTIONS = [("中文", "zh"), ("English", "en")]
SNAKE_COLOR_OPTIONS = [("绿色", GREEN), ("蓝色", BLUE), ("黄色", (255,200,0)), ("紫色", (180,0,180))]
SPEED_OPTIONS = [("慢", 6), ("中", 10), ("快", 16)]
DIFFICULTY_OPTIONS = [("包裹", "wrap"), ("不包裹", "wall")]

# 默认设置（移除 maximize 项）
settings = {
    "lang": "zh",
    "snake_color_idx": 0,
    "speed_idx": 1,        # 对应 SPEED_OPTIONS
    "difficulty_idx": 0,   # 对应 DIFFICULTY_OPTIONS
}

def update_dimensions_from_cell():
    global WIDTH, HEIGHT
    WIDTH = CELL_SIZE * GRID_W
    HEIGHT = CELL_SIZE * GRID_H

# 新增：根据窗口大小计算偏移（居中，不拉伸）
def update_offsets(win_w, win_h):
    global OFFSET_X, OFFSET_Y
    OFFSET_X = (win_w - WIDTH) // 2 if win_w > WIDTH else 0
    OFFSET_Y = (win_h - HEIGHT) // 2 if win_h > HEIGHT else 0

# 新增：查找可用的中文字体（Windows 常见路径优先）
def find_chinese_font():
    # 常见 Windows 字体文件名（按优先级）
    candidates = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyh.ttf",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\arialuni.ttf",
        r"C:\Windows\Fonts\msjh.ttc",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # 如果没有直接文件，尝试通过 pygame 的字体名匹配
    try:
        available = pygame.font.get_fonts()
        names_to_try = ("msyh", "microsoftyahei", "simhei", "simsun", "arialunicode", "arialuni")
        for name in names_to_try:
            match = pygame.font.match_font(name)
            if match:
                return match
    except Exception:
        pass
    return None

def random_food(snake):
    while True:
        pos = (random.randrange(GRID_W), random.randrange(GRID_H))
        if pos not in snake:
            return pos

def draw_cell(surface, pos, color):
    x, y = pos
    rect = pygame.Rect(OFFSET_X + x * CELL_SIZE, OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)

def draw_grid(surface):
    # 使用偏移并只绘制网格区域，避免拉伸
    for x in range(GRID_W + 1):
        start = (OFFSET_X + x * CELL_SIZE, OFFSET_Y)
        end = (OFFSET_X + x * CELL_SIZE, OFFSET_Y + HEIGHT)
        pygame.draw.line(surface, (40,40,40), start, end)
    for y in range(GRID_H + 1):
        start = (OFFSET_X, OFFSET_Y + y * CELL_SIZE)
        end = (OFFSET_X + WIDTH, OFFSET_Y + y * CELL_SIZE)
        pygame.draw.line(surface, (40,40,40), start, end)

def render_text(font, text, lang):
    # 简单语言支持：中文/英文切换（只在固定文本处使用）
    if lang == "en":
        mapping = {
            "贪吃蛇":"Snake",
            "按 空格 / 回车 开始    Esc 退出":"Press Space/Enter to start    Esc to quit",
            "方向键 或 WASD 控制移动":"Arrow keys or WASD to move",
            "分数:":"Score:",
            "游戏结束 - 按 R 重玩，Esc 退出":"Game Over - R to restart, Esc to quit",
            "开始":"Start",
            "设置":"Settings",
            "退出":"Quit",
            "语言":"Language",
            "蛇颜色":"Snake Color",
            "速度":"Speed",
            "难度":"Difficulty",
            "最大化适配":"Maximize adapt",
            "开":"On",
            "关":"Off",
            "返回":"Back (Enter)"
        }
    else:
        mapping = {k:k for k in [
            "贪吃蛇","按 空格 / 回车 开始    Esc 退出","方向键 或 WASD 控制移动",
            "分数:","游戏结束 - 按 R 重玩，Esc 退出",
            "开始","设置","退出","语言","蛇颜色","速度","难度","最大化适配","开","关","返回"
        ]}
    return mapping.get(text, text)

def game_loop():
    global CELL_SIZE, WIDTH, HEIGHT
    pygame.init()
    pygame.font.init()

    flags = pygame.RESIZABLE
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("贪吃蛇")
    clock = pygame.time.Clock()

    # 使用可用的中文字体（若找不到再使用默认字体）
    font_path = find_chinese_font()
    if font_path:
        font = pygame.font.Font(font_path, FONT_SZ)
    else:
        font = pygame.font.Font(None, FONT_SZ)

    title_font = pygame.font.Font(font_path if font_path else None, FONT_SZ + 12)
    small_font = pygame.font.Font(font_path if font_path else None, max(12, FONT_SZ - 6))

    # 初始化偏移与窗口大小跟踪
    win_w, win_h = screen.get_size()
    CELL_SIZE = max(4, min(win_w // GRID_W, win_h // GRID_H))
    update_dimensions_from_cell()
    update_offsets(win_w, win_h)
    prev_size = (win_w, win_h)

    # --- 主开始菜单（含“设置”选项） ---
    menu_items = ["start", "settings", "quit"]
    menu_idx = 0
    in_menu = True
    pygame.mouse.set_visible(True)

    while in_menu:
        # 获取当前窗口尺寸 / 计算布局
        win_w, win_h = screen.get_size()
        center_x, center_y = win_w // 2, win_h // 2

        # 生成渲染文字与可点击区域（每帧刷新，保证响应窗口尺寸变化）
        item_labels = [
            render_text(font, "开始", settings["lang"]),
            render_text(font, "设置", settings["lang"]),
            render_text(font, "退出", settings["lang"]),
        ]
        item_surfs = [small_font.render(lbl, True, WHITE) for lbl in item_labels]
        item_rects = [s.get_rect(center=(center_x, center_y - 20 + i*32)) for i, s in enumerate(item_surfs)]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                # 菜单响应窗口大小变化
                win_w, win_h = event.w, event.h
                screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
                CELL_SIZE = max(4, min(win_w // GRID_W, win_h // GRID_H))
                update_dimensions_from_cell()
                update_offsets(win_w, win_h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key in (pygame.K_UP,):
                    menu_idx = (menu_idx - 1) % len(menu_items)
                elif event.key in (pygame.K_DOWN,):
                    menu_idx = (menu_idx + 1) % len(menu_items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = menu_items[menu_idx]
                    if choice == "start":
                        in_menu = False
                    elif choice == "quit":
                        pygame.quit(); sys.exit()
                    elif choice == "settings":
                        open_settings(screen, title_font, small_font)
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                # hover 影响高亮
                hover_idx = None
                for i, rect in enumerate(item_rects):
                    if rect.collidepoint(mx, my):
                        hover_idx = i
                        break
                if hover_idx is not None:
                    menu_idx = hover_idx
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, rect in enumerate(item_rects):
                    if rect.collidepoint(mx, my):
                        choice = menu_items[i]
                        if choice == "start":
                            in_menu = False
                        elif choice == "quit":
                            pygame.quit(); sys.exit()
                        elif choice == "settings":
                            open_settings(screen, title_font, small_font)
                        break

        # 绘制菜单（响应 hover / keyboard 高亮）
        screen.fill(BLACK)
        title_surf = title_font.render(render_text(font, "贪吃蛇", settings["lang"]), True, WHITE)
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, center_y - 80)))

        for i, surf in enumerate(item_surfs):
            color = WHITE if i == menu_idx else (160,160,160)
            # 重新渲染带颜色文本，保证高亮色正确
            surf = small_font.render(item_labels[i], True, color)
            rect = surf.get_rect(center=(center_x, center_y - 20 + i*32))
            screen.blit(surf, rect)

        pygame.display.flip()
        clock.tick(30)
    # --- 菜单结束，进入游戏 ---

    # 应用设置
    snake_color = SNAKE_COLOR_OPTIONS[settings["snake_color_idx"]][1]
    base_speed = SPEED_OPTIONS[settings["speed_idx"]][1]
    difficulty = DIFFICULTY_OPTIONS[settings["difficulty_idx"]][1]

    # 初始蛇和食物（head first，身体在 head 的下方，配合初始方向 (0,-1) 向上）
    snake = [(GRID_W//2, GRID_H//2 + i) for i in range(3)]  # head first
    direction = (0, -1)  # 上
    food = random_food(snake)
    score = 0
    alive = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # 窗口调整/最大化事件：重新计算 CELL_SIZE 与画布尺寸
            if event.type == pygame.VIDEORESIZE:
                win_w, win_h = event.w, event.h
                screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
                CELL_SIZE = max(4, min(win_w // GRID_W, win_h // GRID_H))
                update_dimensions_from_cell()
                update_offsets(win_w, win_h)
                prev_size = (win_w, win_h)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if alive:
                    if event.key in (pygame.K_w, pygame.K_UP) and direction != (0, 1):
                        direction = (0, -1)
                    elif event.key in (pygame.K_s, pygame.K_DOWN) and direction != (0, -1):
                        direction = (0, 1)
                    elif event.key in (pygame.K_a, pygame.K_LEFT) and direction != (1, 0):
                        direction = (-1, 0)
                    elif event.key in (pygame.K_d, pygame.K_RIGHT) and direction != (-1, 0):
                        direction = (1, 0)
                else:
                    if event.key == pygame.K_r:
                        return  # 结束当前循环以重启游戏

        if alive:
            # 移动（依据难度决定是否包裹）
            head = snake[0]
            new_x = head[0] + direction[0]
            new_y = head[1] + direction[1]
            if difficulty == "wrap":
                new_head = (new_x % GRID_W, new_y % GRID_H)
            else:
                # 碰到边界即死亡
                if not (0 <= new_x < GRID_W and 0 <= new_y < GRID_H):
                    alive = False
                    new_head = (new_x, new_y)
                else:
                    new_head = (new_x, new_y)

            # 撞到自己判断
            if new_head in snake:
                alive = False
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    food = random_food(snake)
                else:
                    snake.pop()

        # 绘制
        screen.fill(BLACK)
        draw_grid(screen)
        # 食物
        draw_cell(screen, food, RED)
        # 蛇
        for i, seg in enumerate(snake):
            color = snake_color if i != 0 else tuple(max(0, c-40) for c in snake_color)  # 头颜色稍深
            draw_cell(screen, seg, color)

        # HUD
        score_label = render_text(font, "分数:", settings["lang"])
        score_surf = font.render(f"{score_label} {score}", True, WHITE)
        screen.blit(score_surf, (8, 8))

        if not alive:
            over_label = render_text(font, "游戏结束 - 按 R 重玩，Esc 退出", settings["lang"])
            over_surf = font.render(over_label, True, WHITE)
            r = over_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(over_surf, r)

        pygame.display.flip()

        # 根据设置速度与得分动态设置帧率（以设置基础速度为基准）
        local_fps = min(60, base_speed + score // 3)
        clock.tick(local_fps)

# 新增：设置界面函数（移除 最大化 选项）
def open_settings(screen, title_font, small_font):
    global CELL_SIZE, WIDTH, HEIGHT
    option_keys = ["lang", "snake_color_idx", "speed_idx", "difficulty_idx"]
    idx = 0
    running = True
    clock = pygame.time.Clock()

    # 英文备用标签（用于 settings["lang"] == 'en' 时显示）
    SNAKE_COLOR_LABELS_EN = ["Green", "Blue", "Yellow", "Purple"]
    SPEED_LABELS_EN = ["Slow", "Medium", "Fast"]
    DIFFICULTY_LABELS_EN = ["Wrap", "Wall"]

    def get_lang_label(code, cur_lang):
        if cur_lang == "en":
            return "Chinese" if code == "zh" else "English"
        else:
            return "中文" if code == "zh" else "English"

    while running:
        win_w, win_h = screen.get_size()
        center_x, center_y = win_w // 2, win_h // 2

        # 构造显示文本（根据当前语言翻译标签）
        label_lang = render_text(small_font, "语言", settings["lang"])
        label_color = render_text(small_font, "蛇颜色", settings["lang"])
        label_speed = render_text(small_font, "速度", settings["lang"])
        label_diff = render_text(small_font, "难度", settings["lang"])
        label_back = render_text(small_font, "返回", settings["lang"])

        # 值文本（根据语言环境选择中/英文显示）
        cur_lang = settings["lang"]
        val_lang = get_lang_label(LANG_OPTIONS[settings["lang"] == "zh" and 0 or 1][1], cur_lang)  # placeholder safe path
        # 更稳的取值：用 settings["lang"] 本身作为当前语言 code；显示当前选择对应名称
        # 生成每项可显示值（语言项特别处理）
        lang_display = get_lang_label(LANG_OPTIONS[0][1], cur_lang) if settings["lang"] == LANG_OPTIONS[0][1] else get_lang_label(LANG_OPTIONS[1][1], cur_lang)
        color_display = (SNAKE_COLOR_OPTIONS[settings["snake_color_idx"]][0]
                         if cur_lang == "zh" else SNAKE_COLOR_LABELS_EN[settings["snake_color_idx"]])
        speed_display = (SPEED_OPTIONS[settings["speed_idx"]][0]
                         if cur_lang == "zh" else SPEED_LABELS_EN[settings["speed_idx"]])
        diff_display = (DIFFICULTY_OPTIONS[settings["difficulty_idx"]][0]
                        if cur_lang == "zh" else DIFFICULTY_LABELS_EN[settings["difficulty_idx"]])

        # 渲染项和位置
        labels = [label_lang, label_color, label_speed, label_diff]
        values = [lang_display, color_display, speed_display, diff_display]
        item_surfs = [small_font.render(l, True, WHITE) for l in labels]
        value_surfs = [small_font.render(v, True, WHITE) for v in values]
        item_rects = [s.get_rect(topleft=(center_x - 160, 140 + i*40)) for i, s in enumerate(item_surfs)]
        value_rects = [vs.get_rect(topleft=(center_x + 20, 140 + i*40)) for i, vs in enumerate(value_surfs)]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                win_w, win_h = event.w, event.h
                screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
                CELL_SIZE = max(4, min(win_w // GRID_W, win_h // GRID_H))
                update_dimensions_from_cell()
                update_offsets(win_w, win_h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_UP,):
                    idx = (idx - 1) % len(option_keys)
                elif event.key in (pygame.K_DOWN,):
                    idx = (idx + 1) % len(option_keys)
                elif event.key in (pygame.K_LEFT,):
                    key = option_keys[idx]
                    if key == "lang":
                        settings["lang"] = LANG_OPTIONS[1][1] if settings["lang"] == LANG_OPTIONS[0][1] else LANG_OPTIONS[0][1]
                    elif key == "snake_color_idx":
                        settings["snake_color_idx"] = (settings["snake_color_idx"] - 1) % len(SNAKE_COLOR_OPTIONS)
                    elif key == "speed_idx":
                        settings["speed_idx"] = (settings["speed_idx"] - 1) % len(SPEED_OPTIONS)
                    elif key == "difficulty_idx":
                        settings["difficulty_idx"] = (settings["difficulty_idx"] - 1) % len(DIFFICULTY_OPTIONS)
                elif event.type == pygame.K_RIGHT or event.key in (pygame.K_RIGHT,):
                    key = option_keys[idx]
                    if key == "lang":
                        settings["lang"] = LANG_OPTIONS[1][1] if settings["lang"] == LANG_OPTIONS[0][1] else LANG_OPTIONS[0][1]
                    elif key == "snake_color_idx":
                        settings["snake_color_idx"] = (settings["snake_color_idx"] + 1) % len(SNAKE_COLOR_OPTIONS)
                    elif key == "speed_idx":
                        settings["speed_idx"] = (settings["speed_idx"] + 1) % len(SPEED_OPTIONS)
                    elif key == "difficulty_idx":
                        settings["difficulty_idx"] = (settings["difficulty_idx"] + 1) % len(DIFFICULTY_OPTIONS)
                elif event.key in (pygame.K_RETURN,):
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                hover = None
                for i, rect in enumerate(item_rects):
                    if rect.collidepoint(mx, my) or value_rects[i].collidepoint(mx, my):
                        hover = i
                        break
                if hover is not None:
                    idx = hover
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                # 左键：下一个；右键：上一个
                for i, rect in enumerate(value_rects):
                    if rect.collidepoint(mx, my):
                        key = option_keys[i]
                        if event.button == 1:  # left
                            if key == "lang":
                                settings["lang"] = LANG_OPTIONS[1][1] if settings["lang"] == LANG_OPTIONS[0][1] else LANG_OPTIONS[0][1]
                            elif key == "snake_color_idx":
                                settings["snake_color_idx"] = (settings["snake_color_idx"] + 1) % len(SNAKE_COLOR_OPTIONS)
                            elif key == "speed_idx":
                                settings["speed_idx"] = (settings["speed_idx"] + 1) % len(SPEED_OPTIONS)
                            elif key == "difficulty_idx":
                                settings["difficulty_idx"] = (settings["difficulty_idx"] + 1) % len(DIFFICULTY_OPTIONS)
                        elif event.button == 3:  # right
                            if key == "lang":
                                settings["lang"] = LANG_OPTIONS[0][1] if settings["lang"] == LANG_OPTIONS[1][1] else LANG_OPTIONS[1][1]
                            elif key == "snake_color_idx":
                                settings["snake_color_idx"] = (settings["snake_color_idx"] - 1) % len(SNAKE_COLOR_OPTIONS)
                            elif key == "speed_idx":
                                settings["speed_idx"] = (settings["speed_idx"] - 1) % len(SPEED_OPTIONS)
                            elif key == "difficulty_idx":
                                settings["difficulty_idx"] = (settings["difficulty_idx"] - 1) % len(DIFFICULTY_OPTIONS)
                        break
                # 点击“返回”区域也可回到主菜单（在窗口底部）
                back_rect = small_font.render(label_back, True, WHITE).get_rect(center=(center_x, win_h - 40))
                if back_rect.collidepoint(mx, my) and event.button == 1:
                    running = False

        # 绘制设置界面
        screen.fill(BLACK)
        title_surf = title_font.render(render_text(small_font, "设置", settings["lang"]), True, WHITE)
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, 60)))

        for i, (lab_surf, val_surf) in enumerate(zip(item_surfs, value_surfs)):
            color = WHITE if i == idx else (180,180,180)
            # 重新渲染以反映高亮
            ks = small_font.render(labels[i], True, color)
            vs = small_font.render(values[i], True, color)
            screen.blit(ks, (center_x - 160, 140 + i*40))
            screen.blit(vs, (center_x + 20, 140 + i*40))
            # 可视化提示：小三角指示当前项
            if i == idx:
                pygame.draw.polygon(screen, color, [(center_x - 180, 140 + i*40 + 8), (center_x - 170, 140 + i*40 + 4), (center_x - 170, 140 + i*40 + 12)])

        hint = small_font.render(label_back, True, (140,140,140))
        screen.blit(hint, hint.get_rect(center=(center_x, win_h - 40)))

        pygame.display.flip()
        clock.tick(30)

def main():
    while True:
        game_loop()

if __name__ == "__main__":
    main()