describe('Dashboard Updates', () => {
    beforeEach(() => {
        // Create mock DOM elements
        document.body.innerHTML = `
            <div id="forecast-plot"></div>
            <div id="last-updated">Last updated: Loading...</div>
        `;
        
        // Mock Plotly
        global.Plotly = {
            update: jest.fn()
        };
        
        // Mock fetch
        global.fetch = jest.fn();
    });
    
    it('should update dashboard with new data', async () => {
        const mockData = {
            actual_load: [1000, 2000, 3000],
            entsoe_forecast: [1100, 2100, 3100],
            model_forecast: [1050, 2050, 3050],
            timestamp: '2024-03-20T12:00:00'
        };
        
        global.fetch.mockResolvedValueOnce({
            json: () => Promise.resolve(mockData)
        });
        
        await updateDashboard();
        
        // Check if Plotly.update was called with correct data
        expect(Plotly.update).toHaveBeenCalled();
        
        // Check if timestamp was updated
        const lastUpdated = document.getElementById('last-updated').textContent;
        expect(lastUpdated).toContain('2024-03-20');
    });
    
    it('should handle API errors gracefully', async () => {
        const consoleSpy = jest.spyOn(console, 'error');
        global.fetch.mockRejectedValueOnce(new Error('API Error'));
        
        await updateDashboard();
        
        expect(consoleSpy).toHaveBeenCalledWith(
            'Error updating dashboard:', 
            expect.any(Error)
        );
    });
}); 