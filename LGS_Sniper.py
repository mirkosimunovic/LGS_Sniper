import sys
import pygame
import numpy as np
from pygame.locals import *
import numpy.random as random

# Classes for the game

class Dome_base(pygame.sprite.Sprite):

	''' Makes the base of the dome '''

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)  # call Sprite constructor
		self.image = pygame.image.load("assets/dome_base_3.png")
		self.rect = self.image.get_rect()
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.rect.topleft = self.area.centerx-290,self.area.centery+200
	def update(self):
		''' update the status '''
		pass 


class Dome_top(pygame.sprite.Sprite):

	''' moves and rotates the Dome of the telescope to aim the object in sky '''

	def __init__(self):
		pygame.sprite.Sprite.__init__(self)  # call Sprite constructor
		self.image = pygame.image.load("assets/dome_top_2.png")
		self.rect = self.image.get_rect()
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.rect.topleft = self.area.centerx-35,self.area.centery+120
		self.angle = 0
		self.moving = 0
		self.original = self.image
		self.angle_step = 1


	def update(self):
		''' update the status '''
		if self.moving:
			self.rotate()


	def rotate(self):
		''' rotate the dome '''
		center = self.rect.center	# record the center position
		limit_angle = self.angle
		self.angle = self.angle + self.angle_step*self.moving
		if self.angle>=50 or self.angle<=-50:
			self.angle = limit_angle

		
		rotate = pygame.transform.rotate
		self.image = rotate(self.original,self.angle)   # rotate from the original to avoid losing quality in each rotation
		self.rect = self.image.get_rect(center=center)	# impose the center position to avoid movement due to rotation

class Galaxy(pygame.sprite.Sprite):

	''' Moves galaxies in the sky '''
	def __init__(self,ypos):
		pygame.sprite.Sprite.__init__(self)
		self.image = self.load_picture()
		self.image = pygame.transform.scale(self.image, (30,30))
		self.rect = self.image.get_rect()
		self.move = 1+ypos*5
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.rect.topleft = 1,self.area.top+ypos*200
		self.outofscreen = False
		self.hit = 0 

	def load_picture(self):

		num = random.random()
		if num<=0.6: return pygame.image.load("assets/galaxy.png")
		elif num>=0.9: return pygame.image.load("assets/GC2.png")
		elif num>=0.8: return pygame.image.load("assets/GC.png")
		elif num>=0.7: return pygame.image.load("assets/galaxy3.png")
		elif num>0.6: return pygame.image.load("assets/galaxy2.png")


	def update(self):
		self.cross()
		if self.outofscreen:  	# Kill the object if out of screen
			self.kill()
		elif self.hit:
			self.kill() 

	def cross(self):			
		''' make the object cross the sky '''
		newpos  = self.rect.move((self.move,0))	
		self.rect = newpos
		if not self.area.contains(newpos):
			self.outofscreen = True


class Cloud(pygame.sprite.Sprite):

	''' Moves clouds in the sky '''
	def __init__(self,ypos):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("assets/cloud.png")
		self.rect = self.image.get_rect()
		self.move = 2
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.rect.topleft = 1,self.area.top+250+ypos*50
		self.outofscreen = False

	def update(self):
		self.cross()
		if self.outofscreen:  	# Kill the object if out of screen
			self.kill()

	def cross(self):			
		''' make the object cross the sky '''
		newpos  = self.rect.move((self.move,0))	
		self.rect = newpos
		if not self.area.contains(newpos):
			self.outofscreen = True			



class Airplane(pygame.sprite.Sprite):

	''' Moves airplanes in the sky '''
	def __init__(self,ypos,left_or_right,screen_size):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("assets/airplane.png")
		self.image = pygame.transform.scale(self.image, (40,20))
		self.rect = self.image.get_rect()
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.outofscreen = False
		self.hit = 0
		self.movey = random.normal(0,2)
		if left_or_right>=0.5:
			self.movex = 4
			self.rect.topleft = 1,self.area.top+150+ypos*50
		else:
			self.movex = -4
			self.rect.topleft = screen_size[0]-50,self.area.top+150+ypos*50
			self.image = pygame.transform.flip(self.image, True, False)  # flip horizontally True, vertically False
		self.angle = np.degrees(np.arctan(self.movey/self.movex))
		self.image = pygame.transform.rotate(self.image,-(self.angle)/2.0)
		

	def update(self):
		self.cross()
		if self.outofscreen:  	# Kill the object if out of screen
			self.kill()
		if self.hit:
			self.kill()

	def cross(self):			
		''' make the object cross the sky '''
		newpos  = self.rect.move((self.movex,self.movey))	
		self.rect = newpos
		if not self.area.contains(newpos):
			self.outofscreen = True		

	def collide(self,target):
		# Returns true if plane hits another plane
		if self.rect.colliderect(target.rect):
			self.hit = 1
			return True			



class Laser(pygame.sprite.Sprite):
	''' Shoots the LGS into the sky '''

	def __init__(self,dome_top):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("assets/Laser.png")
		self.image = pygame.transform.scale(self.image, (4,50))
		self.original = self.image
		# self.rect = self.image.get_rect()
		self.angle = dome_top.angle
		screen = pygame.display.get_surface()	
		self.area = screen.get_rect()
		print ("angle =",self.angle)
		self.speed = self.get_speed()
		self.outofscreen = False

		rotate = pygame.transform.rotate
		self.image = rotate(self.original,self.angle)   # rotate from the original to avoid losing quality in each rotation
		self.rect = self.image.get_rect()	# impose the center position to avoid movement due to rotation
		self.rect.topleft = self.area.centerx-self.angle, self.area.centery+60
		self.ontarget = 0


	def update(self):
		self.trace()
		if self.outofscreen:	# Kill the laser beam if out of screen
			self.kill()
		elif self.ontarget:
			self.kill()

	def trace(self):
		''' make the laser beam move in the sky '''
		newpos = self.rect.move(self.speed)
		self.rect = newpos
		if not self.area.contains(newpos):
			self.outofscreen = True


	def get_speed(self):
		angle = self.angle
		y_speed = -60.
		x_speed = np.tan(np.radians(angle))*y_speed
		return [x_speed,y_speed]
		

	def collide(self,target):
		# Returns true if laser hits a target in sky 
		if self.rect.colliderect(target.rect):
			self.ontarget = 1
			return True





def main():

	pygame.init()

	screen_size = (650,600)
	screen = pygame.display.set_mode(screen_size)	
	pygame.display.set_caption("LGS Sniper")
	pygame.mouse.set_visible(0)

	# Create the background
	background = pygame.Surface(screen.get_size()).convert()
	background.fill((1,1,1))

	# Display some text
	font = pygame.font.Font(None, 25)
	#text = font.render("Data Points: ", 1, (0, 0, 255))
	text = font.render("<LEFT, RIGHT> Move <SPACE> Shoot   ", 1, (0, 255, 255))
	textpos = text.get_rect()
	textpos.centerx = background.get_rect().centerx
	background.blit(text, textpos)


	# Make stars
	N_stars = 1000
	stars_x = np.random.rand(N_stars)*screen_size[0]
	stars_y = np.random.rand(N_stars)*screen_size[1]
	stars_vel = 0.5
	color_stars = 255, 255, 255 # Color: white


	# Display the background
	screen.blit(background,(0,0))
	pygame.display.flip()

	# Create objects
	clock = pygame.time.Clock()
	dome_top = Dome_top()
	dome_base = Dome_base()
	galaxy = Galaxy(0)


	# Print fps on screen
	def update_fps():
		fps = str(int(clock.get_fps()))
		fps = 'fps='+fps
		fps_text = font.render(fps, 1, pygame.Color("coral"))
		return fps_text
	
	allsprites = pygame.sprite.RenderPlain((dome_top,dome_base,galaxy))

	# Main Loop
	play = True
	while play:
		clock.tick(25)

		# Handle Input Events
		for event in pygame.event.get():
			if event.type == QUIT:
				play = False
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				play = False
			elif event.type == KEYDOWN and event.key == K_SPACE:
				laser = Laser(dome_top)	
				allsprites.add(laser) 	
			elif event.type == KEYDOWN and event.key == K_LEFT:
				dome_top.moving = 1
			elif event.type == KEYDOWN and event.key == K_RIGHT:
				dome_top.moving = -1
			elif not event.type == KEYDOWN:
				dome_top.moving = 0

		# Make more galaxies
		num = random.random()
		if num>=0.98:
			ypos = random.random()
			galaxy = Galaxy(ypos)
			allsprites.add(galaxy)


		# Make clouds
		num = random.random()
		if num>=0.99:
			ypos = random.random()
			cloud = Cloud(ypos)
			allsprites.add(cloud)

		# Make airplanes
		num = random.random()
		if num>=0.995:
			ypos = random.random()
			left_or_right = random.random()
			plane = Airplane(ypos,left_or_right,screen_size)
			allsprites.add(plane)



		# Handle Laser Hit events ###
		for inst in allsprites.sprites():
			if type(inst).__name__ == 'Laser':
				for inst2 in allsprites.sprites():
					if type(inst2).__name__ == 'Galaxy':
						if inst.collide(inst2):
							inst2.hit = 1
							break
					elif type(inst2).__name__ == 'Cloud':
						if inst.collide(inst2):
							break
					elif type(inst2).__name__ == 'Airplane':
						if inst.collide(inst2):
							inst2.hit = 1
							break

		# Handle Airplane crashes
		for inst in allsprites.sprites():
			if type(inst).__name__ == 'Airplane':
				for inst2 in allsprites.sprites():
					if type(inst2).__name__ == 'Airplane':
						if inst.movex == -inst2.movex:
							if inst.collide(inst2):							
								inst2.hit = 1
								break


		# Draw the stars
		stars_x = stars_x+stars_vel % screen_size[0]
		stars_x = stars_x + random.normal(0,0.05,size=len(stars_x))
		stars_y = stars_y + random.normal(0,0.05,size=len(stars_x))
		for i in range(N_stars):								
			pygame.draw.line(screen,color_stars,(stars_x[i],stars_y[i]),(stars_x[i],stars_y[i]))

		

		# Draw everythin
		
		# for inst in allsprites.sprites():    # uncomment if want to blit only on rect of objects
		# 	pos = inst.rect
		# 	screen.blit(background,pos,pos)
		
		screen.blit(background,(0,0))
		# Draw the stars
		stars_x = (stars_x+stars_vel) % screen_size[0]
		for i in range(N_stars):								
			pygame.draw.line(screen,color_stars,(stars_x[i],stars_y[i]),(stars_x[i],stars_y[i]))		
		# Draw the sprites	
		allsprites.update()
		allsprites.draw(screen)
		screen.blit(dome_base.image,dome_base.rect)

		# Print fps on screen
		screen.blit(update_fps(), (10,0))

		pygame.display.flip()

	pygame.quit()

if __name__ == '__main__':
	main()





	




						
