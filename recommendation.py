"""A tiny categorical Naive Bayes model. No external services or ML packages.
Seed examples are hand-authored SYNTHETIC preference labels, not family research.
Explicit 'We enjoyed this' feedback adds genuine local examples. No accuracy claim.
"""
from collections import Counter,defaultdict
import math

SEEDS=[
(('active','outdoors','10'),'Football'),(('active','outdoors','20'),'Football'),(('playful','outdoors','20'),'Football'),(('active','outdoors','5'),'Football'),
(('calm','indoors','10'),'Majlis Delivery'),(('playful','indoors','10'),'Majlis Delivery'),(('calm','outdoors','10'),'Majlis Delivery'),(('playful','outdoors','10'),'Majlis Delivery'),
(('playful','indoors','5'),'Falcon Freeze'),(('playful','indoors','10'),'Falcon Freeze'),(('playful','outdoors','5'),'Falcon Freeze'),(('active','indoors','5'),'Falcon Freeze'),
(('active','indoors','10'),'Dune Steps'),(('active','indoors','20'),'Dune Steps'),(('active','outdoors','10'),'Dune Steps'),(('playful','outdoors','20'),'Dune Steps'),
(('calm','indoors','5'),'Family Story Relay'),(('calm','indoors','10'),'Family Story Relay'),(('calm','indoors','20'),'Family Story Relay'),(('calm','outdoors','20'),'Family Story Relay')]

class FamilyRecommender:
    def __init__(self,feedback=()):
        self.classes=Counter();self.counts=defaultdict(Counter);self.values=[set() for _ in range(3)]
        for context,game in SEEDS+list(feedback):
            if len(context)!=3 or game not in {g for _,g in SEEDS}:continue
            self.classes[game]+=1
            for i,value in enumerate(context):self.values[i].add(str(value));self.counts[(game,i)][str(value)]+=1
    def suggest(self,context):
        if len(context)!=3:raise ValueError('Supply energy, space and available minutes.')
        total=sum(self.classes.values());ranks=[]
        for game,count in self.classes.items():
            if game=='Football' and context[1]=='indoors':continue
            score=math.log((count+1)/(total+len(self.classes)))
            for i,value in enumerate(context):score+=math.log((self.counts[(game,i)][str(value)]+1)/(count+len(self.values[i])))
            ranks.append((score,game))
        return max(ranks)[1]
