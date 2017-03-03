from scene import *
import sound
import ui
import random
# import math
import sys
from datetime import datetime

sys.path.insert(0, './lib')
from game_menu import MenuScene

A = Action
screen_size = get_screen_size()
min_screen_axis = min(get_screen_size())

ALPHA = 0.0


class Live(SpriteNode):
	def __init__(self, **kwargs):
		SpriteNode.__init__(self, 'plf:HudHeart_full', **kwargs)
		self.full = True

	def __setattr__(self, name, value):
		SpriteNode.__setattr__(self, name, value)
		if name == 'full' and not value:
				self.texture = Texture('plf:HudHeart_empty')
				sound.play_effect('game:Error')


class controlPanel(Node):
	def __init__(self, size, scale, **kwargs):
		Node.__init__(self, **kwargs)
		shape=ui.Path.rect(0, 0, size[0], size[1])
		self.scale = scale
		self.bg=ShapeNode(path=shape, fill_color='#73ff55', alpha=ALPHA, parent=self)
		self.bg.anchor_point = (0.5, 0.5)
		
		self.test_left = 5
		self.current_test = None
		
		font=('Marker Felt',40)
		self.score_label = LabelNode(parent=self, font=font)
		self.score_label.anchor_point = (0, 0.5)
		self.score_label.text = ''
		self.score_label.color ='#e00fb2'
		self.score_label.position = (-390,0)
		self.score = 0
		
		self.level_label = LabelNode(parent=self,font=font)
		self.level_label.anchor_point = (0, 0.5)
		self.level_label.text = ''
		self.level_label.color ='#e00fb2'
		self.level_label.position = (190,0)
		self.level = 1
		
		self.lives=[]
		for i in range(0,3):
			l = Live(parent=self)
			l.anchor_point = (0.5, 0.5)
			l.position = (-100+(50*i), 0)
			self.lives.append(l)
		self.lives_count = len(self.lives)
		
	def __setattr__(self, name, value):
		Node.__setattr__(self, name, value)
		if name == 'lives_count' and value < 3:
			self.lives[value].full=False
		elif name == 'score':
			self.score_label.text = 'Score: '+str(value)
		elif name == 'level':
			self.level_label.text = 'Level: '+str(value)
			
class Key(SpriteNode):
	def __init__(self, type, number, **kwargs):
		self.type = type
		self.number = number
		self.scale = 1.25
		self.selected = False
		if type == 'number':
			SpriteNode.__init__(self, 'plf:Hud'+str(number), **kwargs)
		elif type == 'delete':
			SpriteNode.__init__(self, 'plf:HudX', **kwargs)
		elif type == 'check':
			SpriteNode.__init__(self,'plf:Tile_SwitchBlue' , **kwargs)
	
	def __setattr__(self, name, value):
		Node.__setattr__(self, name, value)
		if name == 'selected':
			if self.number > -2:
				self.run_action(A.scale_to(0.5 if value else 1.25, 0.15))
			elif value:
				self.texture = Texture('plf:Tile_SwitchBlue_pressed')
			else:
				self.texture = Texture('plf:Tile_SwitchBlue')
			
				
class keyPanel(Node):
	def __init__(self, orientation, size, scale, **kwargs):
		Node.__init__(self, **kwargs)
		shape=ui.Path.rect(0, 0, size[0], size[1])
		self.scale = scale
		self.bg=ShapeNode(path=shape, fill_color='#5590ff', alpha=ALPHA, parent=self)
		self.bg.anchor_point = (0.5, 0.5)
		
		self.keys = []
		for i in range(0, 12):
			if i < 10:
				k = Key(parent=self, type='number', number=i)
			elif i == 10:
				k = Key(parent=self, type='delete', number=-1)
			else:
				k = Key(parent=self, type='check', number=-2)
			k.anchor_point = (0.5, 0.5)
			pos_long = -350+(65*i)
			if orientation == 'portrait':
				k.position = (pos_long, 0)
			else:
				k.position = (0, - pos_long)
			self.keys.append(k)
		
		
class Row(Node):
	def __init__(self, size, scale, **kwargs):
		Node.__init__(self, **kwargs)
		shape=ui.Path.rect(0, 0, size[0], size[1])
		self.scale = scale
		self.bg=ShapeNode(path=shape, fill_color='#ff5555', alpha=ALPHA, parent=self)
		self.bg.anchor_point = (0, 0.5)
		
		font = ('Bradley Hand',100)
		self.equation_label = LabelNode(parent=self, font=font)
		self.equation_label.anchor_point = (0, 0.5)
		self.equation_label.text = ''
		self.equation_label.color ='#bd0094'
		self.equation_label.position = (0,0)
		
		self.clear = True
		
		self.x = 0
		self.y = 0
		self.z = '?'
		
	def __setattr__(self, name, value):
		Node.__setattr__(self, name, value)
		if name == 'clear' and value:
			self.equation_label.text = ''
			self.x = 0
			self.y = 0
			self.z = '?'
		elif name == 'clear' and not value:
			self.equation_label.text = str(self.x)+' + '+str(self.y)+' = '+str(self.z)
		elif name == 'z' and not self.clear:
			self.equation_label.text = str(self.x)+' + '+str(self.y)+' = '+str(value)
			
		
class Canvas(Node):
	def __init__(self, size, scale, **kwargs):
		Node.__init__(self, **kwargs)
		shape=ui.Path.rect(0, 0, size[0], size[1])
		self.scale = scale
		self.bg=ShapeNode(path=shape, fill_color='#5590ff', alpha=ALPHA, parent=self)
		self.bg.anchor_point = (0.5, 1)
		
		self.rows = []
		for i in range (0, 5):
			pos = -600+(130*i)
			r = Row(parent=self, size=(920,120), scale=self.scale)
			r.position = (-390, pos)
			self.rows.append(r)
			
class BaseScene (Scene):
	def setup(self):
		self.root_node = Node(parent=self)
		self.reset_scene()
		self.run_action(A.sequence(A.wait(0.5), A.call(self.show_start_menu)))
		self.did_change_size()
	
	
	def did_change_size(self):
		self.bg.position = (self.size.w/2, self.size.h/2)
		bg_scaled_h = (self.bg.size.h*self.bg.scale)
		top_bg = (self.size.h + bg_scaled_h)/2
		self.control_panel.position = (self.size.w/2+(self.size.w/25), top_bg-(bg_scaled_h/7))
		
		if self.key_panel:
			self.key_panel.remove_from_parent()
		kp_size = self.resize_key_panel()
		o = self.get_orientation()
		self.key_panel = keyPanel(parent=self.root_node, orientation=o, size=kp_size, scale=self.bg.scale)
		if o == 'portrait':
			self.key_panel.position = ((self.size.w/2), (self.size.h-self.bg.size.h)/2)
		else:
			self.key_panel.position = (self.bg.position.x + (self.bg.size.w/2), self.size.h/2)
		self.canvas.position = (self.size.w/2+(self.size.w/25) , top_bg-(bg_scaled_h/5.3))
	
	
	def update(self):
		pass
	
	def get_key_pressed(self, touch):
		touch_pos = self.key_panel.point_from_scene(touch.location)
		# print('%s - %s' % (touch_pos, self.key_panel.keys[0].position))
		for k in self.key_panel.keys:
			if k.frame.contains_point(touch_pos):
				k.selected = True
				return k
				
		
	def touch_began(self, touch):
		k = self.get_key_pressed(touch)
		t = self.control_panel.current_test
		if k:
			if k.number > -1:
				sound.play_effect('game:Click_1')
				if t.z == '?':
					t.z = k.number
				elif len(str(t.z))<4:
					t.z = (t.z*10)+k.number
			elif k.number == -1:
					t.z = '?'
			else:
				sound.play_effect('game:Ding_3')
				if t.z is not '?':
					if t.x + t.y == t.z:
						self.control_panel.score = self.control_panel.score + self.control_panel.level
						self.generate_test()
					else:
						t.z = '?'
						self.control_panel.lives_count -= 1
			
	
	def touch_moved(self, touch):
		pass
	
	def touch_ended(self, touch):
		for k in self.key_panel.keys:
			if k.selected == True:
				k.selected = False
		if self.control_panel.lives_count == 0:
			self.show_game_over_menu()
		
		
	def clean_up(self):
		self.bg.remove_from_parent()
		self.control_panel.remove_from_parent()
		self.key_panel.remove_from_parent()
		self.canvas.remove_from_parent()
		
	def reset_scene(self):
		if hasattr(self, 'bg'):
			self.clean_up()
		self.background_color = '#af3cb3'
		
		self.bg = SpriteNode('res/bg.png',parent=self.root_node)
		self.bg.anchor_point = (0.5,0.5)
		self.bg.scale = 1 / (max(self.bg.size.w+10, self.bg.size.h+10) / min_screen_axis)
		
		cp_size = (self.bg.size.w - (self.bg.size.w/8), 50)
		self.control_panel = controlPanel(parent=self.root_node, size=cp_size, scale=self.bg.scale)
		
		kp_size = self.resize_key_panel()
		o = self.get_orientation()
		self.key_panel = keyPanel(parent=self.root_node, orientation=o, size=kp_size, scale=self.bg.scale)
	
		self.canvas = Canvas(parent=self.root_node, size=(780,680), scale=self.bg.scale)
		
		self.did_change_size()
		
		
	def generate_test(self):
		self.control_panel.test_left -= 1
		if self.control_panel.test_left >= 0:
			self.control_panel.current_test = self.canvas.rows[self.control_panel.test_left]
			random.seed(datetime.now())
			self.control_panel.current_test.x = random.randint(0, 10*self.control_panel.level)
			random.seed(datetime.now())
			self.control_panel.current_test.y = random.randint(0, 10*self.control_panel.level)
			self.control_panel.current_test.z = '?'
			self.control_panel.current_test.clear = False
		else:
			for r in self.canvas.rows:
				r.clear = True
			self.control_panel.level +=1
			self.control_panel.test_left = 5
			self.generate_test()
		
		
	def new_game(self):
		self.root_node.run_action(A.sequence(A.fade_to(0, 0.35), A.remove()))
		self.score = 0
		
		self.root_node = Node(parent=self)
		self.root_node.scale = 0
		self.reset_scene()
		
		self.root_node.run_action(A.scale_to(1, 0.35, 1))
		sound.play_effect('digital:ZapThreeToneUp')
		self.generate_test()
		
		
	def	show_start_menu(self):
		self.paused = True
		self.menu = MenuScene('My Little Maths Game', 'For clever little kids!', ['New Game'])
		self.present_modal_scene(self.menu)
		
		
	def show_game_over_menu(self):
		self.paused = True
		self.menu = MenuScene('Game Over', 'Score: %i' % (self.control_panel.score), ['New Game'])
		self.present_modal_scene(self.menu)
	
	
	def menu_button_selected(self, title):
		if title in ('New Game'):
			self.dismiss_modal_scene()
			self.menu = None
			self.paused = False
			if title == 'New Game':
				self.new_game()


	def get_orientation(self):
		o = ''
		if self.size.w >= self.size.h:
			o = 'landscape'
		else:
			o = 'portrait'
		return o
		
		
	def resize_key_panel(self):
		size =(0,0)
		kp_size_short = 100
		kp_size_long = min(self.size.w, self.size.h)
		if self.get_orientation() == 'portrait':
			size = (kp_size_long, kp_size_short)
		else:
			size = (kp_size_short, kp_size_long)
		return size
		
		
if __name__ == '__main__':
	run(BaseScene(), show_fps=False)
