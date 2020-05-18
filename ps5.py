# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name:
# Collaborators:
# Time:

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz


#-----------------------------------------------------------------------

#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
# Do not change this code
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
          #  pubdate = pubdate.astimezone(pytz.timezone('EST'))
          #  pubdate.replace(tzinfo=None)
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret

#======================
# Data structure design
#======================

# Problem 1

# TODO: NewsStory
class NewsStory(object):
  def __init__(self, guid, title, description, link, pubdate):
    self.guid = guid
    self.title = title
    self.description = description
    self.link = link
    self.pubdate = pubdate

  def get_guid(self):
    self.guid = str(self.guid)
    return self.guid
    
  def get_title(self):
    self.title = str(self.title)
    return self.title

  def get_description(self):
    self.description = str(self.description)
    return self.description

  def get_link(self):
    self.link = str(self.link)
    return self.link
  
  def get_pubdate(self):
    # self.pubdate = datetime.strptime(datetime.strftime(self.pubdate,"%Y, %m, %d, %H, %M, %S"), "%Y, %m, %d, %H, %M, %S")
    return self.pubdate

#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        # DO NOT CHANGE THIS!
        raise NotImplementedError
        
        ### story is the argument used to compare with phrase, ex. title

# PHRASE TRIGGERS

# Problem 2
# TODO: PhraseTrigger
## create abstract class
from abc import ABC, abstractmethod

class PhraseTrigger(Trigger,ABC):
  def __init__(self, phrase):
    self.phrase = phrase

  @abstractmethod 
  def is_phrase_in(self, text):
    # remove all punctuation with space
    for word in text:
      if word in string.punctuation: 
        text = text.replace(word, " ")
    # split text by space
    text = text.split(" ")
    # convert list into string
    t = []
    for x in text:
      if x != '':
        t.append(x)
   
    plain_text = " ".join(t)
    self.phrase = self.phrase.lower()
    phrase_list = self.phrase.split(" ")

    result = True
    # every word in phrase should be exactly the same as in story
    for word in phrase_list:
      if word not in t:
        result = False
    # entirety and appears consecutively
    if self.phrase not in plain_text:
      result = False

    return result


  
# Problem 3
# TODO: TitleTrigger
class TitleTrigger(PhraseTrigger):
  def __init__(self, phrase):
    super().__init__(phrase)
    
  def add_title(self, story):
    text = NewsStory.get_title(story).lower()
    return text

  def is_phrase_in(self, story):
    text = self.add_title(story)
    result = super().is_phrase_in(text)
    return result

  def evaluate(self, story):
    return self.is_phrase_in(story)
    




# Problem 4
# TODO: DescriptionTrigger
class DescriptionTrigger(PhraseTrigger):
  def __init__(self, phrase):
    super().__init__(phrase)

  def add_description(self,story):
    text = NewsStory.get_description(story).lower()
    return text
  
  def is_phrase_in(self, story):
    text = self.add_description(story)
    print (text)
    result = super().is_phrase_in(text)
    return result

  def evaluate(self, story):
    return self.is_phrase_in(story)

# TIME TRIGGERS

# Problem 5
# TODO: TimeTrigger
# Constructor:
#        Input: Time has to be in EST and in the format of "%d %b %Y %H:%M:%S".
#        Convert time from string to a datetime before saving it as an attribute.
class TimeTrigger(Trigger,ABC):
  def __init__(self, time):
    self.time = datetime.strptime(time, "%d %b %Y %H:%M:%S")
    self.time = self.time.replace(tzinfo=pytz.timezone("EST"))
    
  

# Problem 6
# TODO: BeforeTrigger and AfterTrigger
class BeforeTrigger(TimeTrigger):
  def __init__(self, time):
    super().__init__(time)

  def is_before (self, story):
    pubdate = NewsStory.get_pubdate(story)
    pubdate = pubdate.replace(tzinfo=pytz.timezone("EST"))
    
    result = False
    if pubdate < self.time:
      result = True
    return result

  def evaluate(self, story):
    return self.is_before(story)


class AfterTrigger(TimeTrigger):  
  def __init__(self, time):
    super().__init__(time)

  def is_after (self, story):
    pubdate = NewsStory.get_pubdate(story)
    pubdate = pubdate.replace(tzinfo=pytz.timezone("EST"))

    result = False
    if pubdate > self.time:
      result = True
    return result

  def evaluate(self, story):
    return self.is_after(story)

# COMPOSITE TRIGGERS
# Problem 7
# TODO: NotTrigger
class NotTrigger(Trigger):
  def __init__(self, other):
    self.other = other
  
  def evaluate(self, story):
    return not self.other.evaluate(story)


# Problem 8
# TODO: AndTrigger
class AndTrigger(Trigger):
  def __init__(self, trigger1, trigger2):
    self.trigger1 = trigger1
    self.trigger2 = trigger2
  def and_triggered(self,story):
    if self.trigger1.evaluate(story) == True and self.trigger2.evaluate(story) == True:
      return True
    else:
      return False

  def evaluate(self, story):
    return self.and_triggered(story)
       
#     


# Problem 9
# TODO: OrTrigger
class OrTrigger(Trigger):
  def __init__(self, trigger1, trigger2):
    self.trigger1 = trigger1
    self.trigger2 = trigger2
  def or_triggered(self, story):
    if self.trigger1.evaluate(story) == False and self.trigger2.evaluate(story) == False:
      return False
    else:
      return True

  def evaluate(self, story):
    return self.or_triggered(story)
    


#======================
# Filtering
#======================

# Problem 10
def filter_stories(stories, triggerlist):
    """
    Takes in a list of NewsStory instances.

    Returns: a list of only the stories for which a trigger in triggerlist fires.
    """
    # TODO: Problem 10
    # This is a placeholder
    # (we're just returning all the stories, with no filtering)
    story_list = []
    for story in stories:
      for trigger in triggerlist:
        if trigger.evaluate(story) == True:
          story_list.append(story)
    stories = story_list
      
    return stories



#======================
# User-Specified Triggers
#======================
# Problem 11
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file

    Returns: a list of trigger objects specified by the trigger configuration
        file.
    """
    # We give you the code to read in the file and eliminate blank lines and
    # comments. You don't need to know how it works for now!
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)
    
    # TODO: Problem 11
    # line is the list of lines that you need to parse and for which you need
    # to build triggers
    # Helper code by myself
    def trans_to_trigger(trigger_line):
        if trigger_line[1] == "TITLE":
          trigger = TitleTrigger(trigger_line[2])
        elif trigger_line[1] == 'DESCRIPTION':
          trigger = DescriptionTrigger(trigger_line[2])
        elif trigger_line[1] == 'BEFORE':
          trigger = BeforeTrigger(trigger_line[2])
        elif trigger_line[1] == 'AFTER':
          trigger = AfterTrigger(trigger_line[2])

        return trigger
    
    def trans_to_trigger1(tri_dict, trigger_line):
        if trigger_line[1] == 'NOT':
          tri_key = trigger_line[2]
          trigger = NotTrigger(tri_dict[tri_key])
        elif trigger_line[1] == 'AND':
          tri_key = trigger_line[2]
          tri_key2 = trigger_line[3]
          trigger = AndTrigger(tri_dict[tri_key],tri_dict[tri_key2])
        elif trigger_line[1] == 'OR':
          tri_key = trigger_line[2]
          tri_key2 = trigger_line[3]
          trigger = OrTrigger(tri_dict[tri_key],tri_dict[tri_key2])

        return trigger
    #helper code end
    
    tri_dict = {}
    trigger_list = []
    for line in lines:
      # seperate line into words
      trigger_line = line.split(",")
      print (trigger_line)
      if trigger_line[0] != 'ADD':
        if trigger_line[1] not in 'NOT, AND, OR':
          trigger = trans_to_trigger(trigger_line)
          tri_dict[trigger_line[0]] = trigger
        else:
          trigger = trans_to_trigger1(tri_dict, trigger_line)
          tri_dict[trigger_line[0]] = trigger
      else:
        add_num = len(trigger_line)-1
        print (add_num)
        n = 1
        while n <= add_num:
          trigger_list.append(tri_dict[trigger_line[n]])
          n += 1
    
    print(lines) # for now, print it so you see what it contains!

    return trigger_list



SLEEPTIME = 120 #seconds -- how often we poll

def main_thread(master):
    # A sample trigger list - you might need to change the phrases to correspond
    # to what is currently in the news
    try:
        t1 = TitleTrigger("election")
        t2 = DescriptionTrigger("Trump")
        t3 = DescriptionTrigger("Clinton")
        t4 = AndTrigger(t2, t3)
        triggerlist = [t1, t4]

        # Problem 11
        # TODO: After implementing read_trigger_config, uncomment this line 
        # triggerlist = read_trigger_config('triggers.txt')
        
        # HELPER CODE - you don't need to understand this!
        # Draws the popup window that displays the filtered stories
        # Retrieves and filters the stories from the RSS feeds
        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT,fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica",14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []
        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title()+"\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:

            print("Polling . . .", end=' ')
            print (1)
            # Get stories from Google's Top Stories RSS news feed
            stories = process("http://news.google.com/news?output=rss")
            print (2)
            # Get stories from Yahoo's Top Stories RSS news feed
            stories.extend(process("http://news.yahoo.com/rss/topstories"))
            print (3)
            stories = filter_stories(stories, triggerlist)
            print (4)
            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)


            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("Some RSS parser")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()
    
    # story = NewsStory('sr','election','ed','ed','2012, 10, 12, 23, 59, 59')
    # print (story.get_pubdate())

    # story2 = 'purple@#$%cow'
    # phrase = 'purple cow'
    # story1 = 'purple    cow'

    # t = "12 Oct 2017 23:59:59"
    
    # trigger1 = TitleTrigger(phrase)
    # print (trigger1.is_phrase_in(story))
    
    # trigger2 = AfterTrigger (t)
    # print (trigger2.is_after(story))
    
    # # y=NotTrigger(trigger2)
    # # print (y.evaluate(story))
    # ortrigger = OrTrigger(trigger1,trigger2)
    # print (ortrigger.evaluate(story))
   
   
    # a = datetime.now()
    # timezone = pytz.timezone("UTC")
    # d = timezone.localize(a)
    # print (a == d)
    # utcnow = pytz.utc.localize(datetime.utcnow())
    # pst = utcnow.astimezone(pytz.timezone("EST"))
    # print (utcnow.tzinfo,pst.tzinfo)
    # print (datetime.utcnow())
    # triggerlist = 'triggers.txt'
    # a = read_trigger_config(triggerlist)
   
   




    

   