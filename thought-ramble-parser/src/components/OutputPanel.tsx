import React from 'react';
import { type ThoughtParseResponse } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Brain, Clock, Target, Hash, Heart, Zap, Meh } from 'lucide-react';

interface OutputPanelProps {
  result: ThoughtParseResponse | null;
  isLoading: boolean;
}

export function OutputPanel({ result, isLoading }: OutputPanelProps) {
  if (isLoading) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-green-600" />
            Parsed Thoughts
          </CardTitle>
        </CardHeader>
        
        <CardContent className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-4">
            <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto"></div>
            <div className="text-sm text-gray-600">Analyzing your thoughts...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!result) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-green-600" />
            Parsed Thoughts
          </CardTitle>
          <CardDescription>
            Results will appear here after processing your text
          </CardDescription>
        </CardHeader>
        
        <CardContent className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-2 text-gray-500">
            <Brain className="w-12 h-12 mx-auto text-gray-300" />
            <div className="text-sm">No analysis yet</div>
            <div className="text-xs">Enter text and click "Parse Thoughts" to begin</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return <Heart className="w-4 h-4 text-green-500" />;
      case 'negative':
        return <Zap className="w-4 h-4 text-red-500" />;
      default:
        return <Meh className="w-4 h-4 text-gray-500" />;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'negative':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getChunkColor = (index: number) => {
    const colors = [
      'border-l-blue-500 bg-blue-50',
      'border-l-green-500 bg-green-50',
      'border-l-purple-500 bg-purple-50',
      'border-l-orange-500 bg-orange-50',
      'border-l-pink-500 bg-pink-50',
      'border-l-indigo-500 bg-indigo-50',
      'border-l-teal-500 bg-teal-50',
      'border-l-red-500 bg-red-50',
    ];
    return colors[index % colors.length];
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="w-5 h-5 text-green-600" />
          Parsed Thoughts
        </CardTitle>
        <CardDescription>
          {result.total_chunks} thought chunks identified in {result.processing_time.toFixed(3)}s
        </CardDescription>
      </CardHeader>
      
      <CardContent className="flex-1 overflow-hidden">
        {/* Metadata */}
        <div className="flex flex-wrap gap-2 mb-4 p-3 bg-gray-50 rounded-lg">
          <Badge variant="secondary" className="flex items-center gap-1">
            <Hash className="w-3 h-3" />
            {result.total_chunks} chunks
          </Badge>
          <Badge variant="secondary" className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {result.processing_time.toFixed(3)}s
          </Badge>
          <Badge variant="secondary" className="flex items-center gap-1">
            <Target className="w-3 h-3" />
            {Math.round(result.metadata.average_chunk_length)} avg chars
          </Badge>
        </div>

        {/* Thought Chunks */}
        <div className="space-y-4 overflow-y-auto flex-1 pr-2">
          {result.chunks.map((chunk, index) => (
            <div
              key={chunk.id}
              className={`p-4 border-l-4 rounded-r-lg ${getChunkColor(index)} transition-all hover:shadow-sm`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-600">
                    Thought #{chunk.id}
                  </span>
                  <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs border ${getSentimentColor(chunk.sentiment)}`}>
                    {getSentimentIcon(chunk.sentiment)}
                    {chunk.sentiment}
                  </div>
                </div>
                <Badge variant="outline" className="text-xs">
                  {Math.round(chunk.confidence * 100)}% confidence
                </Badge>
              </div>
              
              <p className="text-sm text-gray-800 leading-relaxed mb-3">
                {chunk.text}
              </p>
              
              {chunk.topic_keywords.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {chunk.topic_keywords.map((keyword, i) => (
                    <Badge key={i} variant="outline" className="text-xs text-gray-600">
                      {keyword}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
