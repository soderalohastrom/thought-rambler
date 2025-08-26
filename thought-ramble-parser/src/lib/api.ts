// API service for thought parsing backend

export interface ThoughtChunk {
  id: number;
  text: string;
  confidence: number;
  start_char: number;
  end_char: number;
  topic_keywords: string[];
  sentiment: 'positive' | 'negative' | 'neutral';
}

export interface ThoughtParseRequest {
  text: string;
  provider?: string;
  model?: string;
}

export interface ThoughtParseResponse {
  chunks: ThoughtChunk[];
  total_chunks: number;
  processing_time: number;
  metadata: {
    input_length: number;
    provider: string;
    model: string;
    average_chunk_length: number;
  };
}

export interface SampleRambles {
  small: string[];
  medium: string[];
  large: string[];
}

class ThoughtParserAPI {
  private baseURL: string;

  constructor(baseURL?: string) {
    // Use environment variable or explicit backend URL
    this.baseURL = baseURL || 
      (typeof window !== 'undefined' && window.location.origin.includes('localhost') 
        ? 'http://localhost:8000' 
        : 'https://backend-g33cbpiu7-soderalohastroms-projects.vercel.app');
  }

  async healthCheck() {
    const response = await fetch(`${this.baseURL}/api/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  async parseThoughts(request: ThoughtParseRequest): Promise<ThoughtParseResponse> {
    const response = await fetch(`${this.baseURL}/api/parse-thoughts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: request.text,
        provider: request.provider || 'openai',
        model: request.model || 'gpt-3.5-turbo',
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(errorData.error || `API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getSampleRambles(): Promise<SampleRambles> {
    const response = await fetch('/data/sample_rambles.json');
    if (!response.ok) {
      throw new Error(`Failed to load sample data: ${response.statusText}`);
    }
    return response.json();
  }

  getRandomSample(samples: string[]): string {
    return samples[Math.floor(Math.random() * samples.length)];
  }
}

export const thoughtParserAPI = new ThoughtParserAPI();
export default thoughtParserAPI;