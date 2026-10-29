"""Rules, evidence validation, scoring and tamper-evident judge reports."""
import hashlib
import hmac
import json
import math
import secrets
from pathlib import Path

GAMES = {
 'Football': {'mode':'Team', 'events':{'goal':1}, 'rules':'Two teams wear distinct colours and visible player numbers. State which goal each team attacks before filming. One point per clearly observed goal (whole ball crosses the goal line between posts). No inferred goals from cheering. Record continuous, non-overlapping possession intervals by player; unknown possession is excluded. MVP is the player with the longest observed possession. Highest goals wins; tie: another short sudden-death round.'},
 'Majlis Delivery': {'mode':'Team', 'events':{'delivery':2, 'drop':-1}, 'rules':'Place a soft object on a tray. Walk from a marked start to the delivery zone and return for the next attempt. Two points for each object delivered while still on the tray; minus one for each drop. No running. Each player has 30 seconds. Teams sum member points. Tie: one additional turn per team.'},
 'Falcon Freeze': {'mode':'Individual', 'events':{'freeze_success':1, 'freeze_movement':-1}, 'rules':'The host says MOVE then FREEZE, alternating. Each FREEZE period lasts 3 seconds. One point for holding still through the full period, minus one for visible body movement during it (breathing/blinking excluded). A freeze period receives exactly one outcome. Judge only audible cues and visible play. Each player has 30 seconds. Tie: another round.'},
 'Dune Steps': {'mode':'Individual', 'events':{'correct_step':1, 'wrong_step':-1}, 'rules':'Place floor markers numbered 1, 2 and 3. Host announces the sequence 1-3-2-1-2-3 before play. One point for each correct next marker reached with either foot, minus one for a wrong marker. After a mistake retry the same target. Stop after completing all six targets or 30 seconds. Tie: another round with the same sequence.'},
 'Family Story Relay': {'mode':'Team', 'events':{'valid_sentence':1}, 'rules':'Assigned words: family, desert, kindness. Each player has 30 seconds to add up to three distinct sentences to the family story. One point per intelligible, coherent sentence containing a different assigned word; each assigned word scores at most once per turn. Record the exact spoken sentence as evidence. No points for repeated or missing words. Teams sum member points. Tie: one extra turn per team.'}
}

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def local_secret(folder):
    folder=Path(folder); folder.mkdir(parents=True, exist_ok=True)
    path=folder/'judge.key'
    if not path.exists(): path.write_bytes(secrets.token_bytes(32))
    return path.read_bytes()

def sign(report, key):
    return {'report':report, 'signature':hmac.new(key,canonical(report),hashlib.sha256).hexdigest()}

def verify(envelope, key):
    if not isinstance(envelope,dict) or not isinstance(envelope.get('report'),dict):
        raise ValueError('Invalid report envelope.')
    expected=sign(envelope['report'],key)['signature']
    if not hmac.compare_digest(expected,str(envelope.get('signature',''))):
        raise ValueError('Report signature invalid. Use a report produced by this installation; edited reports are rejected.')
    return envelope['report']

def number(value, lo, hi):
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or not lo <= value <= hi:
        raise ValueError('Evidence contains an invalid number or timestamp.')
    return value

def validate(report, game, players, turn_player):
    """Reject malformed evidence before any score is changed. Model never sets totals."""
    if report.get('game') != game: raise ValueError('Report is for a different game.')
    if report.get('status') not in ('ok','uncertain'): raise ValueError('Missing judging status.')
    duration=number(report.get('duration_seconds'),0.01,300)
    if not isinstance(report.get('summary'),str): raise ValueError('Missing summary.')
    if not isinstance(report.get('events'),list) or len(report['events'])>200: raise ValueError('Invalid events.')
    if not isinstance(report.get('limitations'),list): raise ValueError('Missing limitations.')
    seen=set()
    for event in report['events']:
        if not isinstance(event,dict) or event.get('kind') not in GAMES[game]['events']: raise ValueError('Invalid event type.')
        if event.get('player') not in players: raise ValueError('Unknown player in report.')
        if game!='Football' and event['player']!=turn_player: raise ValueError('Evidence does not belong to the active player.')
        number(event.get('time'),0,duration)
        number(event.get('confidence'),0,1)
        if not isinstance(event.get('evidence'),str) or len(event['evidence'].strip())<5: raise ValueError('Missing event evidence.')
        identity=(event['kind'],event['player'],event['time'])
        if identity in seen: raise ValueError('Duplicate event in report.')
        seen.add(identity)
    kinds=[e['kind'] for e in report['events']]
    if game=='Family Story Relay' and kinds.count('valid_sentence')>3:
        raise ValueError('Story Relay cannot award more than three sentences per turn.')
    if game=='Dune Steps' and kinds.count('correct_step')>6:
        raise ValueError('Dune Steps has only six targets per turn.')
    intervals=report.get('possession',[])
    if not isinstance(intervals,list) or len(intervals)>1000: raise ValueError('Invalid possession intervals.')
    end=0
    for item in sorted(intervals,key=lambda x:x.get('start',-1)):
        if game!='Football' or item.get('player') not in players: raise ValueError('Invalid possession player/game.')
        start=number(item.get('start'),0,duration); stop=number(item.get('end'),0,duration)
        if start<end or stop<=start: raise ValueError('Possession intervals overlap or have invalid duration.')
        number(item.get('confidence'),0,1)
        end=stop
    return report

def score(report, players):
    points={p:0 for p in players}; possession={p:0.0 for p in players}
    if report['status']!='ok': return points,possession
    for e in report['events']:
        if e['confidence']>=0.75: points[e['player']]+=GAMES[report['game']]['events'][e['kind']]
    for p in report.get('possession',[]):
        if p['confidence']>=0.75: possession[p['player']]+=p['end']-p['start']
    return points,possession
