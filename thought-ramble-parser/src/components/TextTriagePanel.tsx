import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { 
  Brain, 
  Link, 
  CheckSquare, 
  AlertTriangle, 
  Recycle,
  Sparkles,
  Trash2,
  MessageSquare,
  Smartphone,
  Coffee
} from 'lucide-react';

interface TriageResult {
  thoughts: any[];
  urls: any[];
  todos: any[];
  quarantine: any[];
  salvaged: any[];
  summary: any;
  processing_log: any[];
}

// Sample data showcasing various capabilities
const SAMPLE_DATA = {
  sms_dump: {
    title: "SMS/Chat Dump",
    icon: <MessageSquare className="w-4 h-4" />,
    text: `need milk eggs bread from store

That hammock website we talked about yesterday had really good deals

asdflkjasdf wtf???

Meeting tomorrow 3pm conf room 2 with Sarah about Q4 projections - bring the latest reports

reddit.com/r/woodworking/comments/xyz123 check this out

don't forget to call mom about thanksgiving plans!!!

jjjjjjjjjjjjjj

That meditation app with the British voice you recommended

Remember to pay electric bill by Friday - URGENT!!!

I've been thinking about that startup idea we discussed last week. The potential for disrupting the market is huge if we can get the right funding

github.com/awesome-python for learning

kelleherinternational.com/careers might have that position

!!!???....,,,,

Should update my resume this weekend and apply

The weather patterns have been really unusual lately suggesting climate change impacts are accelerating faster than predicted`
  },
  mixed_thoughts: {
    title: "Mixed Thoughts & URLs",
    icon: <Brain className="w-4 h-4" />,
    text: `I was reading about quantum computing yesterday and it's fascinating how qubits can exist in superposition

Check out that blue bird social media site for the latest AI news

https://arxiv.org/abs/2301.00234 groundbreaking paper on LLMs

TODO: research competitive analysis for new product launch
TODO: schedule dentist appointment - tooth still hurts
TODO: buy anniversary gift

The interconnectedness of global supply chains means that disruptions in one region can cascade through the entire system

qwertyuiop[]

That news aggregator site with the orange logo has interesting discussions

My philosophy on life has evolved considerably. Where I once sought certainty, I now embrace the ambiguity and complexity of existence

$#@%^&*()_+ 

linkedin.com/in/johndoe connect with this person

Need to explore machine learning frameworks - tensorflow vs pytorch comparison`
  },
  creative_stream: {
    title: "Creative Stream",
    icon: <Coffee className="w-4 h-4" />,
    text: `Morning pages style writing just letting thoughts flow

that online marketplace for handmade goods where artists sell stuff

Story idea: protagonist discovers they can hear other people's thoughts but only when those people are typing

🎨🎭🎪🎯🎮

URGENT: Submit grant proposal by end of week
Meeting notes from yesterday attached below
Call Jennifer re: partnership opportunity

The way sunlight filters through autumn leaves reminds me of stained glass windows in old cathedrals

zzzzzzzzzzzzz

Philosophy meets technology at the intersection of human consciousness and artificial intelligence

medium.com/@thoughtleader/future-of-work

When we consider the implications of quantum mechanics on free will, we must question whether determinism is merely an illusion

stack overflow has that solution we need

The creative process is inherently messy - embracing chaos leads to breakthrough innovations

Remember: pick up dry cleaning, renew car registration, book flights for conference

aaaaaaaaaaaaaa

That video platform owned by Google has tutorials on everything`
  }
};

export function TextTriagePanel() {
  const [inputText, setInputText] = useState('');
  const [results, setResults] = useState<TriageResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleTriage = async () => {
    setIsLoading(true);
    try {
      // Use relative URL for Vercel deployment
      const baseUrl = process.env.NODE_ENV === 'production' 
        ? '/api/triage-process' 
        : 'http://localhost:8000/api/triage/process';
        
      const response = await fetch(baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          mode: 'full',
          enable_llm: false
        }),
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Triage error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSampleData = (key: keyof typeof SAMPLE_DATA) => {
    setInputText(SAMPLE_DATA[key].text);
    setResults(null); // Clear previous results
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            Intelligent Text Triage System
          </CardTitle>
          <p className="text-sm text-gray-600 mt-2">
            Transform messy text dumps into organized thoughts, URLs, TODOs, and more
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            {Object.entries(SAMPLE_DATA).map(([key, sample]) => (
              <Button
                key={key}
                onClick={() => loadSampleData(key as keyof typeof SAMPLE_DATA)}
                variant="outline"
                size="sm"
                className="justify-start"
              >
                {sample.icon}
                <span className="ml-2">{sample.title}</span>
              </Button>
            ))}
          </div>
          
          <Textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Paste your text dump here (SMS messages, notes, random thoughts, URLs)..."
            className="min-h-[250px] font-mono text-sm"
          />
          
          <div className="flex justify-between items-center">
            <div className="text-xs text-gray-500">
              {inputText.length} characters
            </div>
            <Button
              onClick={handleTriage}
              disabled={!inputText || isLoading}
              className="bg-purple-600 hover:bg-purple-700"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Processing...
                </>
              ) : (
                <>
                  <Filter className="w-4 h-4 mr-2" />
                  Triage Text
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results Section */}
      {results && (
        <>
          {/* Summary Stats */}
          <Card className="border-purple-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <AlertTriangle className="w-4 h-4 text-purple-600" />
                Processing Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {results.summary.total_chunks}
                  </div>
                  <div className="text-xs text-gray-600">Total Chunks</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {(results.summary.quality_metrics?.clean_ratio * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-600">Clean Ratio</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {results.urls.filter(u => u.type === 'inferred').length}
                  </div>
                  <div className="text-xs text-gray-600">URLs Inferred</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {results.todos.length}
                  </div>
                  <div className="text-xs text-gray-600">TODOs Found</div>
                </div>
              </div>
              
              {results.summary.recommendations?.length > 0 && (
                <div className="mt-4 p-3 bg-purple-50 rounded-lg">
                  <div className="text-xs font-semibold mb-2">AI Recommendations:</div>
                  <ul className="text-xs space-y-1">
                    {results.summary.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-1">
                        <span className="text-purple-600">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Thoughts */}
            {results.thoughts.length > 0 && (
              <Card className="border-blue-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Brain className="w-4 h-4 text-blue-600" />
                    Coherent Thoughts ({results.thoughts.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {results.thoughts.map((thought, i) => (
                      <div key={i} className="p-2 bg-blue-50 rounded text-xs">
                        {thought.original_text?.substring(0, 150)}
                        {thought.original_text?.length > 150 && '...'}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* URLs */}
            {results.urls.length > 0 && (
              <Card className="border-green-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Link className="w-4 h-4 text-green-600" />
                    URLs Found ({results.urls.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {results.urls.map((url, i) => (
                      <div key={i} className="p-2 bg-green-50 rounded">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge 
                            variant={url.type === 'explicit' ? 'default' : 'secondary'}
                            className="text-xs"
                          >
                            {url.type}
                          </Badge>
                          {url.confidence && (
                            <Badge 
                              variant="outline" 
                              className={`text-xs ${
                                url.confidence === 'high' ? 'text-green-600' :
                                url.confidence === 'medium' ? 'text-yellow-600' :
                                'text-gray-600'
                              }`}
                            >
                              {url.confidence}
                            </Badge>
                          )}
                        </div>
                        <div className="text-xs font-mono text-blue-600 truncate">
                          {url.urls?.[0]?.url || url.url || ''}
                        </div>
                        {url.type === 'inferred' && (
                          <div className="text-xs text-gray-500 mt-1 italic">
                            From: "{url.original_text?.substring(0, 50)}"
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* TODOs */}
            {results.todos.length > 0 && (
              <Card className="border-yellow-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <CheckSquare className="w-4 h-4 text-yellow-600" />
                    Action Items ({results.todos.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {results.todos.map((todo, i) => (
                      <div key={i} className="p-2 bg-yellow-50 rounded">
                        <div className="flex items-start gap-2">
                          <div className={`mt-0.5 ${
                            todo.urgency === 'high' ? 'text-red-500' : 
                            todo.urgency === 'low' ? 'text-gray-400' : 
                            'text-yellow-500'
                          }`}>
                            {todo.urgency === 'high' ? '🔴' : 
                             todo.urgency === 'low' ? '🟢' : '🟡'}
                          </div>
                          <div className="flex-1">
                            <div className="text-xs">{todo.action}</div>
                            <Badge 
                              variant="outline" 
                              className="text-xs mt-1"
                            >
                              {todo.urgency} priority
                            </Badge>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Salvaged */}
            {results.salvaged.length > 0 && (
              <Card className="border-orange-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Recycle className="w-4 h-4 text-orange-600" />
                    Salvaged Parts ({results.salvaged.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {results.salvaged.map((item, i) => (
                      <div key={i} className="p-2 bg-orange-50 rounded">
                        <div className="text-xs mb-1 font-semibold">Recovered:</div>
                        <div className="text-xs text-gray-700">
                          {item.salvaged_parts?.join(' | ')}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          Quality: {(item.quality_score * 100).toFixed(0)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Quarantine */}
            {results.quarantine.length > 0 && (
              <Card className="border-red-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Trash2 className="w-4 h-4 text-red-600" />
                    Quarantine ({results.quarantine.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {results.quarantine.map((item, i) => (
                      <div key={i} className="p-2 bg-red-50 rounded">
                        <div className="text-xs font-mono text-gray-600 mb-1">
                          "{item.original_text?.substring(0, 30)}"
                        </div>
                        <div className="text-xs text-red-600">
                          Issues: {item.issues?.join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </>
      )}
    </div>
  );
}

// Add missing import
import { Filter } from 'lucide-react';