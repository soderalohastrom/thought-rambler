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
  Trash2
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

export function TextTriagePanel() {
  const [inputText, setInputText] = useState('');
  const [results, setResults] = useState<TriageResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleTriage = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/triage/process', {
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

  const loadSampleData = () => {
    const sample = `need milk and eggs

https://amazon.com/dp/B08XYZ123

that hammock site we looked at yesterday

asdflkjasdf

meeting at 3pm conf room 2 with Sarah about Q4 projections

reddit.com/r/woodworking/comments/abc123

don't forget to call mom about thanksgiving

blue bird social media thing has the news

Remember to pay electric bill by Friday!!!

kelleherinternational.com careers page

jjjjjjjjjjjjj

I should really update my resume this weekend`;
    
    setInputText(sample);
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-4 space-y-4">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            Intelligent Text Triage
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button
              onClick={loadSampleData}
              variant="outline"
              size="sm"
            >
              Load Sample SMS Dump
            </Button>
            <Button
              onClick={handleTriage}
              disabled={!inputText || isLoading}
              className="bg-purple-600 hover:bg-purple-700"
            >
              {isLoading ? 'Processing...' : 'Triage Text'}
            </Button>
          </div>
          
          <Textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Paste your text dump here (SMS messages, notes, random thoughts)..."
            className="min-h-[200px] font-mono text-sm"
          />
        </CardContent>
      </Card>

      {/* Results Section */}
      {results && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Thoughts */}
          <Card className="border-blue-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Brain className="w-4 h-4 text-blue-600" />
                Thoughts ({results.thoughts.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {results.thoughts.map((thought, i) => (
                  <div key={i} className="p-2 bg-blue-50 rounded text-xs">
                    {thought.original_text?.substring(0, 100)}...
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* URLs */}
          <Card className="border-green-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Link className="w-4 h-4 text-green-600" />
                URLs ({results.urls.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {results.urls.map((url, i) => (
                  <div key={i} className="p-2 bg-green-50 rounded">
                    <div className="flex items-center gap-2">
                      <Badge variant={url.type === 'explicit' ? 'default' : 'secondary'}>
                        {url.type}
                      </Badge>
                      <span className="text-xs font-mono truncate">
                        {url.urls?.[0]?.url || url.url || url.original_text}
                      </span>
                    </div>
                    {url.confidence && (
                      <div className="text-xs text-gray-600 mt-1">
                        Confidence: {url.confidence}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* TODOs */}
          <Card className="border-yellow-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <CheckSquare className="w-4 h-4 text-yellow-600" />
                TODOs ({results.todos.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {results.todos.map((todo, i) => (
                  <div key={i} className="p-2 bg-yellow-50 rounded">
                    <div className="text-xs">{todo.action}</div>
                    <Badge 
                      variant="outline" 
                      className={`text-xs mt-1 ${
                        todo.urgency === 'high' ? 'text-red-600' : 
                        todo.urgency === 'low' ? 'text-gray-600' : 
                        'text-yellow-600'
                      }`}
                    >
                      {todo.urgency}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Salvaged */}
          {results.salvaged.length > 0 && (
            <Card className="border-orange-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Recycle className="w-4 h-4 text-orange-600" />
                  Salvaged ({results.salvaged.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {results.salvaged.map((item, i) => (
                    <div key={i} className="p-2 bg-orange-50 rounded text-xs">
                      {item.salvaged_parts?.join(' | ')}
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
                <div className="space-y-2">
                  {results.quarantine.map((item, i) => (
                    <div key={i} className="p-2 bg-red-50 rounded">
                      <div className="text-xs text-gray-600">
                        {item.original_text?.substring(0, 30)}...
                      </div>
                      <div className="text-xs text-red-600 mt-1">
                        {item.issues?.join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Summary */}
          <Card className="border-purple-200 md:col-span-2 lg:col-span-3">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <AlertTriangle className="w-4 h-4 text-purple-600" />
                Processing Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-xs text-gray-600">Total Chunks</div>
                  <div className="text-xl font-bold">{results.summary.total_chunks}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-600">Clean Ratio</div>
                  <div className="text-xl font-bold">
                    {(results.summary.quality_metrics?.clean_ratio * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-600">Salvage Rate</div>
                  <div className="text-xl font-bold">
                    {(results.summary.quality_metrics?.salvage_ratio * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-600">URL Inference</div>
                  <div className="text-xl font-bold">
                    {(results.summary.quality_metrics?.url_inference_ratio * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
              
              {results.summary.recommendations?.length > 0 && (
                <div className="mt-4 p-3 bg-purple-50 rounded">
                  <div className="text-xs font-semibold mb-2">Recommendations:</div>
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
        </div>
      )}
    </div>
  );
}