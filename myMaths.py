from scene import *
import sound
import ui
# import random
# import math
import sys

sys.path.insert(0, './lib')
from game_menu import MenuScene

A = Action
screen_size = get_screen_size()
min_screen_axis = min(get_screen_size())

class Live(SpriteNode):
	def __init__(self, **kwargs):
		SpriteNode.__init__(self, 'plf:HudHeart_full', **kwargs)
		self.full = True

	def __setattr__(self, name, value):
		SpriteNode.__setattr__(self, name, value)
		if name == 'full':
			if not value:
				#self.run_action(A.scale_to(0.75 if value else 1, 0.15))
				self.texture = Texture('plf:HudHeart_empty')
				sound.play_effect('game:Error')


class controlPanel(Node):
	def __init__(self, size, scale, **kwargs):
		Node.__init__(self, **kwargs)
		shape=ui.Path.rect(0, 0, size[0], size[1])
		self.scale = scale
		self.bg=ShapeNode(path=shape, fill_color='#5590ff', alpha=0.0, parent=self)
		self.bg.anchor_point = (0.5, 0.5)
		
		font=('Marker Felt',40)
		self.score_label = LabelNode(parent=self,font=font)
		self.score_label.anchor_point = (0, 0.5)
		self.score_label.text = 'Score: 0'
		self.score_label.color ='#e00fb2'
		self.score_label.position = (-390,0)
		
		self.lives=[]
		for i in range(0,3):
			l = Live(parent=self)
			l.anchor_point = (0.5, 0.5)
			l.position = (-100+(50*i), 0)
			self.lives.append(l)
		self.lives_count = len(self.lives)
		
	def __setattr__(self, name, value):
		Node.__setattr__(self, name, value)
		if name == 'lives_count' and value<3:
			self.lives[value].full=False

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
	
	
	def update(self):
		pass
	
	def touch_began(self, touch):
		pass
	
	def touch_moved(self, touch):
		pass
	
	def touch_ended(self, touch):
		self.control_panel.lives_count -= 1
		if self.control_panel.lives_count == 0:
			self.show_game_over_menu()
		
		
	def reset_scene(self):
		self.background_color = '#af3cb3'
		
		self.bg = SpriteNode('res/bg.png',parent=self.root_node)
		self.bg.anchor_point = (0.5,0.5)
		self.bg.scale = 1 / (max(self.bg.size.w+10, self.bg.size.h+10) / min_screen_axis)
		
		size = (self.bg.size.w - (self.bg.size.w/8), 50)
		self.control_panel = controlPanel(parent=self.root_node, size=size, scale=self.bg.scale)
		self.did_change_size()
		
		
	def new_game(self):
		self.root_node.run_action(A.sequence(A.fade_to(0, 0.35), A.remove()))
		self.score = 0
		#self.score_label.text = '0'
		
		self.root_node = Node(parent=self)
		self.root_node.scale = 0
		self.reset_scene()
		
		self.root_node.run_action(A.scale_to(1, 0.35, 1))
		sound.play_effect('digital:ZapThreeToneUp')
		pass
		
	def	show_start_menu(self):
		self.paused = True
		self.menu = MenuScene('My Little Maths Game', 'For clever little kids!', ['New Game'])
		self.present_modal_scene(self.menu)
		
	def show_game_over_menu(self):
		self.paused = True
		self.menu = MenuScene('Game Over', 'Score: %i' % (0), ['New Game'])
		self.present_modal_scene(self.menu)
	
	def menu_button_selected(self, title):
		if title in ('New Game'):
			self.dismiss_modal_scene()
			self.menu = None
			self.paused = False
			if title == 'New Game':
				self.new_game()

if __name__ == '__main__':
	run(BaseScene(), show_fps=False)
