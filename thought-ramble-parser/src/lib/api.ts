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
  enable_llm?: boolean;
}

export interface VerboseLog {
  step: string;
  cloudflare_endpoint?: string;
  model?: string;
  provider?: string;
  input_text_length?: number;
  input_text_preview?: string;
  timestamp?: number;
  request_prepared?: boolean;
  request_sent?: boolean;
  response_received?: boolean;
  response_parsed?: boolean;
  chunks_created?: boolean;
  error?: string | null;
  warnings?: string[];
  request_data?: any;
  request_body_size?: number;
  request_headers?: any;
  request_start_time?: number;
  request_duration?: number;
  response_status?: number;
  response_headers?: any;
  response_body_size?: number;
  response_text_preview?: string;
  response_is_json?: boolean;
  response_json_keys?: string[];
  response_success?: boolean;
  cloudflare_response_full?: any;
  thought_groups_count?: number;
  thought_groups_raw?: any[];
  first_group_detail?: any;
  final_chunks_count?: number;
  chunks_created_count?: number;
  cloudflare_metadata?: any;
  http_error_code?: number;
  http_error_reason?: string;
  error_response_body?: string;
  error_type?: string;
  traceback?: string;
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
    llm_enhanced?: boolean;
  };
  // Extended logging data for debugging
  verbose_log?: VerboseLog;
  llm_details?: {
    cloudflare_success?: boolean;
    model_used?: string;
    coherence_score?: number;
    analysis_full?: any;
    processing_time_cloudflare?: number;
  };
  request_info?: {
    endpoint_used?: string;
    fallback_occurred?: boolean;
    request_timestamp?: number;
    processing_steps?: string[];
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
    // Use environment variable or current origin for unified deployment
    this.baseURL = baseURL || 
      (typeof window !== 'undefined' && window.location.origin.includes('localhost') 
        ? 'http://localhost:8000' 
        : window.location.origin);
  }

  async healthCheck() {
    const response = await fetch(`${this.baseURL}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  async parseThoughts(request: ThoughtParseRequest): Promise<ThoughtParseResponse> {
    // Choose endpoint based on LLM enhancement setting
    const endpoint = request.enable_llm ? '/api/parse-thoughts-llm' : '/api/parse-thoughts';
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: request.text,
        provider: request.provider || 'openai',
        model: request.model || 'gpt-3.5-turbo',
        enable_llm: request.enable_llm || false,
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