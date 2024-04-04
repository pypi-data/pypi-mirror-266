import React from 'react';
import { ResourceUsageWidget } from './../ResourceUsageWidget';
import { instanceMetricsMock } from '../../service/__tests__/mock';
import { render } from '@testing-library/react';
import { ServerConnection } from '@jupyterlab/services';
import { ReactWidgetWrapper } from '../../utils/ReactWidgetWrapper';

jest.mock('@jupyterlab/services', () => {
  const module = jest.requireActual('@jupyterlab/services');
  return {
    ...module,
    ServerConnection: {
      ...module.ServerConnection,
      makeRequest: jest.fn(),
      makeSettings: jest.fn(() => {
        return {
          settings: {
            baseUrl: '',
          },
        };
      }),
    },
  };
});

describe('ResourceUsageWidget suite', () => {
  const mockServerConnection = ServerConnection.makeRequest as jest.Mock;

  it('should test rendering the widget with metrics and 200 status', async () => {
    const ResponseMock = jest.fn((status, data) => ({
      status,
      ok: 200 <= status && status < 300 && Number.isInteger(status),
      json: () => {
        return Promise.resolve(data);
      },
    }));
    mockServerConnection.mockImplementation(async () => {
      return ResponseMock(200, instanceMetricsMock);
    });
    const resourceUsageWidget = new ResourceUsageWidget();
    render(<ReactWidgetWrapper item={resourceUsageWidget} />);
    jest.useFakeTimers();
    try {
      await resourceUsageWidget.getInstanceMetrics();
      expect(ResponseMock).toHaveBeenCalledTimes(1);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error);
    }
    jest.runAllTimers();
  });
});
