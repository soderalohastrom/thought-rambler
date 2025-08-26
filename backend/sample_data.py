# Sample thought rambles for testing the parser

SMALL_RAMBLES = [
    "Okay so I need to pick up groceries but first I should call Mom about dinner plans this weekend and oh wait did I remember to set that doctor appointment I was supposed to call yesterday maybe I should write this stuff down somewhere.",
    
    "I'm thinking about that meeting tomorrow and whether I prepared enough slides but then again Sarah said the presentation doesn't need to be too formal so maybe I'm overthinking this whole thing I always do that.",
    
    "Need to remember to pay the electric bill before Thursday and also check if the car needs an oil change soon I think it's been like four months since the last one or was it three I should really keep better track of these things."
]

MEDIUM_RAMBLES = [
    "Alright team so we're looking at the Q3 numbers and they're not terrible but not great either we need to pivot on the marketing strategy maybe look at social media differently I was thinking about that conversation with Sarah yesterday about customer retention and how we're losing people in the onboarding process maybe we should simplify the signup flow or add more tutorial videos I don't know but something needs to change because our CAC is getting too high and the investors are starting to ask questions about our growth projections for next year.",
    
    "So I'm standing in the kitchen this morning making coffee and I realize I forgot to submit that report that was due yesterday which is just typical me procrastinating until the last minute but then I remembered that Jennifer said the deadline was flexible so maybe it's not a big deal but I should probably send an email explaining the delay anyway and while I'm thinking about it I need to schedule that dentist appointment I've been putting off for months my teeth have been feeling weird lately especially when I drink cold stuff which reminds me I should probably cut back on the ice cream.",
    
    "The weather's been really strange lately like yesterday it was sunny and today it's raining cats and dogs which makes me think about climate change and how unpredictable everything's becoming my garden is suffering too the tomatoes aren't ripening properly and the basil is getting these weird brown spots maybe I should research organic fungicides or just accept that this isn't going to be a great harvest year I mean my neighbor Steve seems to have no problems with his garden but he probably uses all those chemical fertilizers that I'm trying to avoid."
]

LARGE_RAMBLES = [
    "Okay so I was driving to work this morning and got stuck in that ridiculous traffic on Highway 101 again which gave me way too much time to think about everything that's going wrong in my life right now like the fact that I still haven't heard back from that job interview two weeks ago which is probably a bad sign but then again the hiring manager did say they were interviewing a lot of candidates so maybe I'm just being paranoid but it's hard not to overthink these things especially when my current job is so stressful and my boss keeps piling more projects on my desk without any additional resources or support and speaking of support I really need to call my therapist and schedule another appointment because I've been feeling overwhelmed lately and that breathing technique she taught me isn't working as well as it used to maybe I need to try meditation or yoga or something I saw this article about mindfulness apps that might help but then again I already have too many apps on my phone and I spend way too much time staring at screens anyway which is probably contributing to my insomnia I've been waking up at three in the morning with my mind racing about all the things I need to do and all the ways I'm falling behind in life like I still haven't finished that online course I paid for six months ago and my kitchen renovation project has been stalled since March because the contractor disappeared and won't return my calls I swear contractors are the worst they promise you the world and then vanish into thin air leaving you with half-finished projects and a huge hole in your budget speaking of budget I need to sit down and actually look at my finances this month because I have a feeling I'm spending way more than I'm making especially with all these subscription services that keep charging my credit card every month I probably have subscriptions I don't even remember signing up for like that meditation app I mentioned earlier ironically enough.",
    
    "You know what's really bothering me is this whole situation at work where they hired this new manager who clearly doesn't understand our department at all and keeps making these arbitrary decisions that make no sense like last week she decided we needed to change our entire project tracking system to some new software that nobody knows how to use and doesn't integrate with any of our existing tools so now we're spending more time figuring out how to log our hours than actually doing any real work and when I tried to explain this to her she just said we need to be more adaptable and embrace change which is corporate speak for shut up and do what I say without questioning anything but the thing is I've been here for five years and I know what works and what doesn't work and this definitely doesn't work but nobody wants to hear that from someone at my level they just want us to smile and nod and pretend everything is fine even when it's obviously not fine and meanwhile our actual productivity is going down the drain because we're all confused and frustrated and spending half our day in meetings about the new system instead of actually using it to get things done and I'm starting to think maybe it's time to update my resume and start looking for something else because this place is becoming toxic and I don't want to be one of those people who stays at a bad job for twenty years just because it's familiar and comfortable even though the thought of job hunting again makes me want to hide under my bed covers and never come out but I know I need to take control of my career instead of just letting things happen to me like I usually do I'm always so passive about these big life decisions but maybe this is the push I needed to finally make a change and do something that actually makes me happy instead of just paying the bills although paying the bills is important too I can't just quit without having something else lined up that would be irresponsible especially with the economy being so uncertain these days."
]

def get_sample_ramble(size: str) -> str:
    """Get a random sample ramble of specified size"""
    import random
    
    if size.lower() == 'small':
        return random.choice(SMALL_RAMBLES)
    elif size.lower() == 'medium':
        return random.choice(MEDIUM_RAMBLES)
    elif size.lower() == 'large':
        return random.choice(LARGE_RAMBLES)
    else:
        return random.choice(SMALL_RAMBLES)

def get_all_samples() -> dict:
    """Get all sample rambles organized by size"""
    return {
        'small': SMALL_RAMBLES,
        'medium': MEDIUM_RAMBLES,
        'large': LARGE_RAMBLES
    }
