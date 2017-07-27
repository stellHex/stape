#encoding: utf-8
import re

'''
TODO:
- add methods for a StapleRun to actually run (run.next, run.end)
- add loop.format
'''

class StapleRun(object):

   def __init__(self, program):
      self.parseIndex = 0
      self.program = program
      self.miniprogram = program
      j=0
      for reg, rep in [
         [r'\\\\', u'∖'],      #start escaping \
         [r'(?<!\\)\[', u'⟦'], #create left groupers
         [r'(?<!\\)\]', u'⟧'], #create right groupers
         [r'\\\[', '['],       #escape [
         [r'\\]', ']'],        #escape ]
         [r'\\\n', u'¶'],      #start escaping newlines
         [r'(\n|^)\s*', u'ɲ'], #start ignoring newlines and leading whitespace
         [ur'ɲ(\\\s)', '\1'],  #escape leading whitespace
         [ur'ɲ', ''],          #finish ignoring newlines and leading whitespace
         [r'\\.', ''],         #ignore other escaped characters
         [u'∖', r'\\'],        #finish escaping \
         [u'¶', '\n'],         #finish escaping newlines
      ]: 
         try: self.miniprogram = re.sub(reg, rep, self.miniprogram)
         except: print reg, rep, j
         j+=1
      self.ipx = 0
      self.buffer = None
      validator0, validator1 = self.miniprogram, None
      while validator0 != validator1:
         validator1 = validator0
         validator0 = re.sub(ur'⟦[^⟦⟧]*⟧','',validator1)
      if re.search(u'⟧|⟦', validator0): 
         print self.miniprogram, validator0, validator1
         raise RuntimeError(u'Invalid program {}; mismatched []!'.format(self.miniprogram))
      self.loop = self.main = self.parse()

   def parse(self):
      program = self.miniprogram
      loop = Loop([], self)
      while True:
         try: char = program[self.parseIndex]
         except IndexError: break
         self.parseIndex+=1
         if char == u'⟦': loop.content.append(self.parse())
         elif char != u'⟧': loop.content.append(char)
         else: break
      loop.adopt()
      return loop

class Loop(object):

   def __init__(self, content, run, parent=None):
      self.dpx = 0
      self.dpv = -1
      self.content = [None] + content
      self.run = run

   @property
   def parent(self):
      '''parent is wrapped so that operations don't try to modify it'''
      print self
      if self.content[0] is None: return None
      else: return self.content[0][0]
   @parent.setter
   def parent(self, val):
      if val is None: self.content[0] = val
      else: self.content[0] = (val,)
      return val
   @parent.deleter
   def parent(self):
      self.parent = None

   def __str__(self): return self.format()
   def __repr__(self): return repr(self.content)

   def __getitem__(self, key):
      return self.content[key%len(self.content)]

   def adopt(self):
      for cell in self.content:
         print type(cell) is Loop, cell
         if type(cell) is Loop:
            cell.parent = self

   def operate(self, op):
      '''Python doesn't do complex anonymous functions, and I don't want to def 30 methods, so I had to resort to to elif hell.
      Sorry.'''
      run = self.run
      arg = self[self.dpx]
      intarg = Loop.toInt(arg)
      oldlen = len(self.content)
      if type(op) is not string:
         return
      elif '<>'.find(op) >= 0 and type(arg) is not tuple:
         indices = [run.ipx%oldlen, self.dpx%oldlen]
         i, j = min(indices), max(indices)
         run.buffer = arg
         self.content[i:j+1] = [Loop(self.content[i+1:j], run, self)]
         newloop = self[i]
         newloop.adopt()
         run.ipx = i
         self.dpx = i
         if op == '<':
            run.ipx = i-1
         else:
            run.loop = newloop
            run.ipx = 0
      elif '=' == op and type(arg) is Loop:
         run.loop = arg
         run.ipx = 0
      elif '-' == op:
         if self is run.main:
            run.end()
            return
         run.loop = self.parent
         run.ipx = run.loop.index(self)
      elif '{' == op and type(arg) is Loop:
         for cell in arg:
            if type(cell) is Loop: cell.parent = self
         if run.ipx%oldlen > self.dpx%oldlen: run.ipx += len(arg.content)+1
         self.content[dpx:dpx+1] = [':']+arg.content[1:]+[':']
         del arg
      elif '}' == op:
         if self is run.main:
            run.end()
            return
         i = self.parent.content.index(self)
         for cell in self:
            if type(cell) is Loop: cell.parent = self.parent
         if self.parent.dpx%len(parent.content) > i: self.parent.dpx += oldlen+1
         run.loop = self.parent
         run.ipx += i
         self.parent[i:i+1] = [':']+self.content[1:]+[':']
         del self
      elif '@' == op:
         if intarg is not None:
            run.ipx += intarg
            self.dpx += intarg
      elif '%' == op:
         if intarg is not None:
            self.dpv = intarg
      elif 'CX'.find(op) >= 0:
         if type(arg) is str: run.buffer = arg
         elif type(arg) is Loop: run.buffer = Loop(arg.content, run)
         else: return
         if op == 'X':
            self.content[self.dpx] = ':'
      elif 'V' == op and run.buffer is not None and type(arg) is not tuple:
         if type(run.buffer) is Loop: run.buffer.parent = self
         self.content[self.dpx] = run.buffer
         run.buffer = None
      elif 'I' == op:
         pass
      elif 'O' == op:
         pass
      elif '#' == op and type(arg) is Loop:
         run.buffer = Loop(Loop.fromInt(intarg), run)
      elif '#' == op and type(arg) is str:
         content = Loop.fromInt(ord(arg))
         while(len(content) < 4): content[1:1] = ['0'] 
         run.buffer = Loop(content, run)
      elif 'M' == op and intarg is not None and -1 < intarg and intarg < 256:
         run.buffer = chr(intarg)
      elif '+' == op:
         run.buffer = Loop(Loop.fromInt(intarg + Loop.toInt(run.buffer)), run)
      elif '*' == op:
         run.buffer = Loop(Loop.fromInt(intarg * Loop.toInt(run.buffer)), run)
         #'''

   @staticmethod
   def toInt(cell):
      if type(cell) is str:
         try: return '-0123456789'.index(cell)-1
         except ValueError: return None
      elif type(cell) is Loop:
         result, neg = 0, 1
         for subcell in cell.content:
            if subcell in '0123456789': result = 10*result + int(subcell)
            elif subcell == '-': neg *= -1
         return result*neg
      elif type(cell) is None:
         return 0
      else:
         raise RuntimeError('Invalid cell "{}" of type "{}"'.format(str(cell),type(cell).__name__))

   @staticmethod
   def fromInt(num):
      return list(str(int(num)))