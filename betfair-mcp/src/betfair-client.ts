import fetch from 'node-fetch';

// Betfair API Configuration
export interface BetfairConfig {
  appKey: string;
  sessionToken: string;
  australian?: boolean;
}

// JSON-RPC Request
interface JsonRpcRequest {
  jsonrpc: '2.0';
  method: string;
  params: Record<string, unknown>;
  id: number;
}

// JSON-RPC Response
interface JsonRpcResponse<T> {
  jsonrpc: '2.0';
  result?: T;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
  id: number;
}

// Betfair API Types
export interface EventType {
  id: string;
  name: string;
}

export interface Competition {
  id: string;
  name: string;
}

export interface Event {
  id: string;
  name: string;
  countryCode?: string;
  timezone?: string;
  venue?: string;
  openDate?: string;
}

export interface MarketCatalogue {
  marketId: string;
  marketName: string;
  totalMatched?: number;
  eventType?: EventType;
  competition?: Competition;
  event?: Event;
  description?: {
    marketType?: string;
    marketTime?: string;
    suspendTime?: string;
    bettingType?: string;
    turnInPlayEnabled?: boolean;
  };
  runners?: RunnerCatalog[];
}

export interface RunnerCatalog {
  selectionId: number;
  runnerName: string;
  sortPriority?: number;
  metadata?: Record<string, string>;
}

export interface MarketBook {
  marketId: string;
  isDelayed?: boolean;
  status?: string;
  betDelay?: number;
  bspReconciled?: boolean;
  complete?: boolean;
  inplay?: boolean;
  numberOfWinners?: number;
  numberOfRunners?: number;
  numberOfActiveRunners?: number;
  lastMatchTime?: string;
  totalMatched?: number;
  totalAvailable?: number;
  crossMatching?: boolean;
  runners?: RunnerBook[];
}

export interface RunnerBook {
  selectionId: number;
  status?: string;
  totalMatched?: number;
  adjustmentFactor?: number;
  lastPriceTraded?: number;
  handicap?: number;
  ex?: {
    availableToBack?: PriceSize[];
    availableToLay?: PriceSize[];
    tradedVolume?: PriceSize[];
  };
}

export interface PriceSize {
  price: number;
  size: number;
}

export interface CurrentOrder {
  betId: string;
  marketId: string;
  selectionId: number;
  handicap?: number;
  priceSize: PriceSize;
  bspLiability?: number;
  side: 'BACK' | 'LAY';
  status: string;
  persistenceType: string;
  orderType: string;
  placedDate: string;
  matchedDate?: string;
  averagePriceMatched?: number;
  sizeMatched?: number;
  sizeRemaining?: number;
  customerStrategyRef?: string;
  customerOrderRef?: string;
}

export interface PlaceOrderResult {
  marketId: string;
  status: string;
  customerRef?: string;
  errorCode?: string;
  instructionReports?: InstructionReport[];
}

export interface InstructionReport {
  status: string;
  errorCode?: string;
  instruction: {
    selectionId: number;
    handicap?: number;
    side: 'BACK' | 'LAY';
    orderType: string;
    limitOrder?: {
      size: number;
      price: number;
      persistenceType: string;
    };
  };
  betId?: string;
  averagePriceMatched?: number;
  sizeMatched?: number;
  placedDate?: string;
}

export interface CancelOrderResult {
  marketId: string;
  status: string;
  customerRef?: string;
  errorCode?: string;
  instructionReports?: CancelInstructionReport[];
}

export interface CancelInstructionReport {
  status: string;
  errorCode?: string;
  instruction: {
    betId: string;
    sizeReduction?: number;
  };
  sizeCancelled?: number;
  cancelledDate?: string;
}

export interface AccountFunds {
  availableToBetBalance?: number;
  exposure?: number;
  retainedCommission?: number;
  exposureLimit?: number;
  discountRate?: number;
  pointsBalance?: number;
  wallet?: string;
}

export interface AccountDetails {
  currencyCode?: string;
  firstName?: string;
  lastName?: string;
  localeCode?: string;
  region?: string;
  timezone?: string;
  discountRate?: number;
  pointsBalance?: number;
  countryCode?: string;
}

export class BetfairClient {
  private readonly appKey: string;
  private readonly sessionToken: string;
  private readonly baseUrl: string;
  private requestId = 0;

  constructor(config: BetfairConfig) {
    this.appKey = config.appKey;
    this.sessionToken = config.sessionToken;
    // Australian exchange uses different endpoint
    this.baseUrl = config.australian 
      ? 'https://api.betfair.com/exchange/betting'
      : 'https://api.betfair.com/exchange/betting';
  }

  private getHeaders(): Record<string, string> {
    return {
      'X-Application': this.appKey,
      'X-Authentication': this.sessionToken,
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
  }

  private async jsonRpc<T>(
    endpoint: string,
    method: string,
    params: Record<string, unknown> = {}
  ): Promise<T> {
    const url = `${endpoint}/json-rpc/v1`;
    
    const request: JsonRpcRequest = {
      jsonrpc: '2.0',
      method,
      params,
      id: ++this.requestId,
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = (await response.json()) as JsonRpcResponse<T>;
    
    if (data.error) {
      throw new Error(`Betfair API Error: ${data.error.message} (code: ${data.error.code})`);
    }

    return data.result as T;
  }

  private async restRequest<T>(
    endpoint: string,
    method: string,
    params: Record<string, unknown> = {}
  ): Promise<T> {
    const url = `${endpoint}/rest/v1.0/${method}/`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }

    return response.json() as Promise<T>;
  }

  // ============ BETTING API ============

  /**
   * List all available event types (sports)
   */
  async listEventTypes(filter: Record<string, unknown> = {}): Promise<EventType[]> {
    return this.jsonRpc<EventType[]>(
      this.baseUrl,
      'SportsAPING/v1.0/listEventTypes',
      { filter }
    );
  }

  /**
   * List competitions for a sport
   */
  async listCompetitions(filter: Record<string, unknown> = {}): Promise<Competition[]> {
    return this.jsonRpc<Competition[]>(
      this.baseUrl,
      'SportsAPING/v1.0/listCompetitions',
      { filter }
    );
  }

  /**
   * List events matching filter
   */
  async listEvents(filter: Record<string, unknown> = {}): Promise<Event[]> {
    return this.jsonRpc<Event[]>(
      this.baseUrl,
      'SportsAPING/v1.0/listEvents',
      { filter }
    );
  }

  /**
   * List market catalogue (available markets)
   */
  async listMarketCatalogue(
    filter: Record<string, unknown>,
    maxResults: number = 100,
    marketProjection: string[] = ['MARKET_DESCRIPTION', 'RUNNER_DESCRIPTION']
  ): Promise<MarketCatalogue[]> {
    return this.jsonRpc<MarketCatalogue[]>(
      this.baseUrl,
      'SportsAPING/v1.0/listMarketCatalogue',
      { filter, maxResults, marketProjection }
    );
  }

  /**
   * Get market prices/odds
   */
  async listMarketBook(
    marketIds: string[],
    priceProjection: Record<string, unknown> = {
      priceData: ['EX_ALL_OFFERS', 'EX_TRADED'],
    }
  ): Promise<MarketBook[]> {
    return this.jsonRpc<MarketBook[]>(
      this.baseUrl,
      'SportsAPING/v1.0/listMarketBook',
      { marketIds, priceProjection }
    );
  }

  /**
   * Place bets
   */
  async placeOrders(
    marketId: string,
    instructions: Array<{
      selectionId: number;
      side: 'BACK' | 'LAY';
      orderType: 'LIMIT' | 'LIMIT_ON_CLOSE' | 'MARKET_ON_CLOSE';
      handicap?: number;
      limitOrder?: {
        size: number;
        price: number;
        persistenceType: 'LAPSE' | 'PERSIST' | 'MARKET_ON_CLOSE';
      };
    }>,
    customerRef?: string
  ): Promise<PlaceOrderResult> {
    return this.jsonRpc<PlaceOrderResult>(
      this.baseUrl,
      'SportsAPING/v1.0/placeOrders',
      { marketId, instructions, customerRef }
    );
  }

  /**
   * Cancel bets
   */
  async cancelOrders(
    marketId: string,
    instructions?: Array<{
      betId: string;
      sizeReduction?: number;
    }>,
    customerRef?: string
  ): Promise<CancelOrderResult> {
    return this.jsonRpc<CancelOrderResult>(
      this.baseUrl,
      'SportsAPING/v1.0/cancelOrders',
      { marketId, instructions, customerRef }
    );
  }

  /**
   * List current/open orders
   */
  async listCurrentOrders(
    betStatus?: string,
    orderBy?: string,
    sortDir?: string,
    fromRecord?: number,
    recordCount?: number
  ): Promise<{ currentOrders: CurrentOrder[]; moreAvailable: boolean }> {
    const params: Record<string, unknown> = {};
    if (betStatus) params.betStatus = betStatus;
    if (orderBy) params.orderBy = orderBy;
    if (sortDir) params.sortDir = sortDir;
    if (fromRecord !== undefined) params.fromRecord = fromRecord;
    if (recordCount !== undefined) params.recordCount = recordCount;

    return this.jsonRpc(
      this.baseUrl,
      'SportsAPING/v1.0/listCurrentOrders',
      params
    );
  }

  // ============ ACCOUNT API ============

  /**
   * Get account balance
   */
  async getAccountFunds(wallet?: string): Promise<AccountFunds> {
    const params: Record<string, unknown> = {};
    if (wallet) params.wallet = wallet;
    
    return this.jsonRpc<AccountFunds>(
      'https://api.betfair.com/exchange/account',
      'AccountAPING/v1.0/getAccountFunds',
      params
    );
  }

  /**
   * Get account details
   */
  async getAccountDetails(): Promise<AccountDetails> {
    return this.jsonRpc<AccountDetails>(
      'https://api.betfair.com/exchange/account',
      'AccountAPING/v1.0/getAccountDetails',
      {}
    );
  }
}
