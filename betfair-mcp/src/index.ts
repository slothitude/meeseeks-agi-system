#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import dotenv from 'dotenv';
import { BetfairClient } from './betfair-client.js';

// Load environment variables
dotenv.config();

// Configuration from environment
const config = {
  appKey: process.env.BETFAIR_APP_KEY || '',
  sessionToken: process.env.BETFAIR_SESSION_TOKEN || '',
  australian: process.env.BETFAIR_AUSTRALIAN === 'true',
};

// Validate configuration
if (!config.appKey || !config.sessionToken) {
  console.error('Error: BETFAIR_APP_KEY and BETFAIR_SESSION_TOKEN must be set');
  console.error('Set them in .env file or environment variables');
  process.exit(1);
}

// Initialize Betfair client
const client = new BetfairClient(config);

// Create MCP server
const server = new Server(
  {
    name: 'betfair-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      // Betting API Tools
      {
        name: 'list_event_types',
        description: 'List all available event types (sports) on Betfair Exchange',
        inputSchema: {
          type: 'object',
          properties: {
            filter: {
              type: 'object',
              description: 'Optional filter criteria',
              properties: {
                textQuery: { type: 'string', description: 'Text to search for' },
                exchangeIds: { 
                  type: 'array', 
                  items: { type: 'string' },
                  description: 'Exchange IDs to filter by (1 = Australian, 0 = Global)'
                },
              },
            },
          },
        },
      },
      {
        name: 'list_competitions',
        description: 'List competitions for a sport/event type on Betfair Exchange',
        inputSchema: {
          type: 'object',
          properties: {
            filter: {
              type: 'object',
              description: 'Filter criteria (include eventTypeIds for specific sport)',
              properties: {
                textQuery: { type: 'string' },
                eventTypeIds: { 
                  type: 'array', 
                  items: { type: 'string' },
                  description: 'Event type IDs (sports) to filter by'
                },
                eventIds: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'Event IDs to filter by',
                },
                marketCountries: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'Countries to filter markets by',
                },
                marketTypeCodes: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'Market type codes (e.g., MATCH_ODDS)',
                },
              },
            },
          },
        },
      },
      {
        name: 'list_events',
        description: 'List events matching filter criteria on Betfair Exchange',
        inputSchema: {
          type: 'object',
          properties: {
            filter: {
              type: 'object',
              description: 'Filter criteria',
              properties: {
                textQuery: { type: 'string' },
                eventTypeIds: { 
                  type: 'array', 
                  items: { type: 'string' },
                  description: 'Event type IDs to filter by'
                },
                eventIds: {
                  type: 'array',
                  items: { type: 'string' },
                },
                competitionIds: {
                  type: 'array',
                  items: { type: 'string' },
                },
                marketStartTime: {
                  type: 'object',
                  properties: {
                    from: { type: 'string', description: 'Start time from (ISO date)' },
                    to: { type: 'string', description: 'Start time to (ISO date)' },
                  },
                },
              },
            },
          },
        },
      },
      {
        name: 'list_market_catalogue',
        description: 'List available markets for events on Betfair Exchange',
        inputSchema: {
          type: 'object',
          properties: {
            filter: {
              type: 'object',
              description: 'Filter criteria (must include eventIds or eventTypeIds)',
              properties: {
                textQuery: { type: 'string' },
                eventTypeIds: { type: 'array', items: { type: 'string' } },
                eventIds: { type: 'array', items: { type: 'string' } },
                competitionIds: { type: 'array', items: { type: 'string' } },
                marketIds: { type: 'array', items: { type: 'string' } },
                marketTypeCodes: { type: 'array', items: { type: 'string' } },
                marketCountries: { type: 'array', items: { type: 'string' } },
                marketStartTime: {
                  type: 'object',
                  properties: {
                    from: { type: 'string' },
                    to: { type: 'string' },
                  },
                },
              },
            },
            maxResults: {
              type: 'number',
              description: 'Maximum number of results (default: 100)',
              default: 100,
            },
            marketProjection: {
              type: 'array',
              items: { 
                type: 'string',
                enum: ['COMPETITION', 'EVENT', 'EVENT_TYPE', 'MARKET_DESCRIPTION', 'RUNNER_DESCRIPTION', 'RUNNER_METADATA']
              },
              description: 'Data to include in response',
              default: ['MARKET_DESCRIPTION', 'RUNNER_DESCRIPTION'],
            },
          },
          required: ['filter'],
        },
      },
      {
        name: 'list_market_book',
        description: 'Get current prices/odds for specified markets on Betfair Exchange',
        inputSchema: {
          type: 'object',
          properties: {
            marketIds: {
              type: 'array',
              items: { type: 'string' },
              description: 'List of market IDs to get prices for',
            },
            priceProjection: {
              type: 'object',
              description: 'What price data to include',
              properties: {
                priceData: {
                  type: 'array',
                  items: {
                    type: 'string',
                    enum: ['SP_AVAILABLE', 'SP_TRADED', 'EX_BEST_OFFERS', 'EX_ALL_OFFERS', 'EX_TRADED'],
                  },
                  default: ['EX_ALL_OFFERS', 'EX_TRADED'],
                },
                exBestOffersOverrides: {
                  type: 'object',
                  properties: {
                    bestPricesDepth: { type: 'number' },
                    rollupModel: { type: 'string' },
                    rollupLimit: { type: 'number' },
                    rollupLiabilityThreshold: { type: 'number' },
                    rollupLiabilityFactor: { type: 'number' },
                  },
                },
                virtualise: { type: 'boolean', default: true },
                rolloverStakes: { type: 'boolean', default: false },
              },
            },
          },
          required: ['marketIds'],
        },
      },
      {
        name: 'place_orders',
        description: 'Place bets on a market on Betfair Exchange (USE WITH CAUTION - REAL MONEY)',
        inputSchema: {
          type: 'object',
          properties: {
            marketId: {
              type: 'string',
              description: 'Market ID to place bets on',
            },
            instructions: {
              type: 'array',
              description: 'List of bet instructions',
              items: {
                type: 'object',
                properties: {
                  selectionId: { type: 'number', description: 'Selection (runner) ID' },
                  side: { type: 'string', enum: ['BACK', 'LAY'], description: 'Back or Lay' },
                  orderType: { type: 'string', enum: ['LIMIT', 'LIMIT_ON_CLOSE', 'MARKET_ON_CLOSE'] },
                  handicap: { type: 'number', description: 'Handicap value (if applicable)' },
                  limitOrder: {
                    type: 'object',
                    properties: {
                      size: { type: 'number', description: 'Stake size' },
                      price: { type: 'number', description: 'Odds price' },
                      persistenceType: { 
                        type: 'string', 
                        enum: ['LAPSE', 'PERSIST', 'MARKET_ON_CLOSE'],
                        description: 'What happens to unmatched portion when market goes in-play'
                      },
                    },
                    required: ['size', 'price', 'persistenceType'],
                  },
                },
                required: ['selectionId', 'side', 'orderType'],
              },
            },
            customerRef: {
              type: 'string',
              description: 'Optional reference for the order batch',
            },
          },
          required: ['marketId', 'instructions'],
        },
      },
      {
        name: 'cancel_orders',
        description: 'Cancel bets on a market on Betfair Exchange',
        inputSchema: {
          type: 'object',
          properties: {
            marketId: {
              type: 'string',
              description: 'Market ID to cancel bets on',
            },
            instructions: {
              type: 'array',
              description: 'List of cancel instructions (omit to cancel all)',
              items: {
                type: 'object',
                properties: {
                  betId: { type: 'string', description: 'Bet ID to cancel' },
                  sizeReduction: { type: 'number', description: 'Amount to reduce (omit for full cancel)' },
                },
                required: ['betId'],
              },
            },
            customerRef: {
              type: 'string',
              description: 'Optional reference for the cancel batch',
            },
          },
          required: ['marketId'],
        },
      },
      {
        name: 'list_current_orders',
        description: 'List current/open orders on Betfair Exchange',
        inputSchema: {
          type: 'object',
          properties: {
            betStatus: {
              type: 'string',
              enum: ['SETTLED', 'VOIDED', 'LAPSED', 'CANCELLED', 'EXECUTION_COMPLETE', 'EXECUTABLE'],
              description: 'Filter by bet status',
            },
            orderBy: {
              type: 'string',
              enum: ['BY_BET', 'BY_MARKET', 'BY_MATCH_TIME', 'BY_PLACE_TIME', 'BY_SETTLED_TIME', 'BY_VOID_TIME'],
              description: 'Order results by',
            },
            sortDir: {
              type: 'string',
              enum: ['EARLIEST_TO_LATEST', 'LATEST_TO_EARLIEST'],
              description: 'Sort direction',
            },
            fromRecord: {
              type: 'number',
              description: 'Start from this record (for pagination)',
            },
            recordCount: {
              type: 'number',
              description: 'Number of records to return (max 1000)',
            },
          },
        },
      },
      // Account API Tools
      {
        name: 'get_account_funds',
        description: 'Get account balance and funds on Betfair Exchange',
        inputSchema: {
          type: 'object',
          properties: {
            wallet: {
              type: 'string',
              description: 'Wallet to query (usually not needed for UK accounts)',
            },
          },
        },
      },
      {
        name: 'get_account_details',
        description: 'Get account details on Betfair Exchange',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result: unknown;

    switch (name) {
      // Betting API
      case 'list_event_types':
        result = await client.listEventTypes((args?.filter as Record<string, unknown>) || {});
        break;

      case 'list_competitions':
        result = await client.listCompetitions((args?.filter as Record<string, unknown>) || {});
        break;

      case 'list_events':
        result = await client.listEvents((args?.filter as Record<string, unknown>) || {});
        break;

      case 'list_market_catalogue':
        result = await client.listMarketCatalogue(
          args?.filter as Record<string, unknown>,
          (args?.maxResults as number) || 100,
          (args?.marketProjection as string[]) || ['MARKET_DESCRIPTION', 'RUNNER_DESCRIPTION']
        );
        break;

      case 'list_market_book':
        result = await client.listMarketBook(
          args?.marketIds as string[],
          (args?.priceProjection as Record<string, unknown>) || {
            priceData: ['EX_ALL_OFFERS', 'EX_TRADED'],
          }
        );
        break;

      case 'place_orders':
        result = await client.placeOrders(
          args?.marketId as string,
          args?.instructions as Array<{
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
          args?.customerRef as string | undefined
        );
        break;

      case 'cancel_orders':
        result = await client.cancelOrders(
          args?.marketId as string,
          args?.instructions as Array<{ betId: string; sizeReduction?: number }> | undefined,
          args?.customerRef as string | undefined
        );
        break;

      case 'list_current_orders':
        result = await client.listCurrentOrders(
          args?.betStatus as string | undefined,
          args?.orderBy as string | undefined,
          args?.sortDir as string | undefined,
          args?.fromRecord as number | undefined,
          args?.recordCount as number | undefined
        );
        break;

      // Account API
      case 'get_account_funds':
        result = await client.getAccountFunds(args?.wallet as string | undefined);
        break;

      case 'get_account_details':
        result = await client.getAccountDetails();
        break;

      default:
        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    throw new McpError(ErrorCode.InternalError, `Betfair API error: ${errorMessage}`);
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Betfair MCP server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
