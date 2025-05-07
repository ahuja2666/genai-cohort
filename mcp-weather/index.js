import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { z } from 'zod';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import axios from 'axios';

const server = new McpServer({
  name: 'My Server',
  version: '1.0.0',
});

server.tool('add', { a: z.number(), b: z.number() }, async function ({ a, b }) {
  const sum = a + b;
  return { content: [{ type: 'text', text: String(sum) }] };
});

server.tool(
  'weather',
  { city: z.string().describe('Name of the city') },
  async function ({ city }) {
    const response = await axios.get(`https://wttr.in/${city}?format=%C+%t`, {
      responseType: 'json',
    });
    return { content: [{ type: 'text', text: JSON.stringify(response.data) }] };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
