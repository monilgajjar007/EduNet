import streamlit as st
import pandas as pd
import random
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Battery Cell Monitor",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StreamlitBatteryCellMonitor:
    def __init__(self):
        self.valid_cell_types = ["lfp", "li-ion", "nicad", "nimh", "lead-acid"]
        self.voltage_map = {
            "lfp": 3.2,
            "li-ion": 3.6,
            "nicad": 1.2,
            "nimh": 1.2,
            "lead-acid": 2.0
        }
        
        # Initialize session state
        if 'cells_data' not in st.session_state:
            st.session_state.cells_data = {}
        if 'cell_counter' not in st.session_state:
            st.session_state.cell_counter = 0

    def add_cell(self, cell_type):
        """Add a new cell to the system"""
        if len(st.session_state.cells_data) >= 8:
            return False, "Maximum 8 cells reached!"
        
        st.session_state.cell_counter += 1
        cell_id = f"cell_{st.session_state.cell_counter}_{cell_type}"
        
        voltage = self.voltage_map.get(cell_type, 3.6)
        
        st.session_state.cells_data[cell_id] = {
            "type": cell_type,
            "voltage": voltage,
            "current": 0.0,
            "temp": round(random.uniform(25, 40), 1),
            "capacity": 0.0,
            "status": "Ready",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return True, f"Added new cell: {cell_id}"

    def remove_cell(self, cell_id):
        """Remove a cell from the system"""
        if cell_id in st.session_state.cells_data:
            del st.session_state.cells_data[cell_id]
            return True, f"Removed cell: {cell_id}"
        return False, "Cell not found!"

    def update_cell_current(self, cell_id, current):
        """Update current for a specific cell"""
        if cell_id in st.session_state.cells_data:
            voltage = st.session_state.cells_data[cell_id]['voltage']
            st.session_state.cells_data[cell_id]["current"] = current
            st.session_state.cells_data[cell_id]["capacity"] = round(voltage * current, 2)
            st.session_state.cells_data[cell_id]["status"] = "Active" if current > 0 else "Standby"
            return True
        return False

    def get_cells_dataframe(self):
        """Convert cells data to pandas DataFrame"""
        if not st.session_state.cells_data:
            return pd.DataFrame()
        
        data = []
        for cell_id, cell_data in st.session_state.cells_data.items():
            row = {"Cell ID": cell_id}
            row.update(cell_data)
            data.append(row)
        
        return pd.DataFrame(data)

    def export_data(self, format='json'):
        """Export cell data in various formats"""
        if format == 'json':
            return json.dumps(st.session_state.cells_data, indent=2)
        elif format == 'csv':
            df = self.get_cells_dataframe()
            return df.to_csv(index=False)

def main():
    monitor = StreamlitBatteryCellMonitor()
    
    # Header
    st.title("🔋 Battery Cell Status Monitor")
    st.markdown("---")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🛠️ Cell Management")
        
        # Add new cell section
        st.subheader("Add New Cell")
        cell_type = st.selectbox(
            "Select Cell Type",
            monitor.valid_cell_types,
            format_func=str.upper
        )
        
        if st.button("➕ Add Cell", type="primary"):
            success, message = monitor.add_cell(cell_type)
            if success:
                st.success(message)
            else:
                st.error(message)
            st.rerun()
        
        # Current cell count
        cell_count = len(st.session_state.cells_data)
        st.info(f"Current cells: {cell_count}/8")
        
        st.markdown("---")
        
        # Bulk operations
        st.subheader("🔄 Bulk Operations")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear All"):
                st.session_state.cells_data = {}
                st.session_state.cell_counter = 0
                st.rerun()
        
        with col2:
            if st.button("🎲 Random Data"):
                for cell_id in st.session_state.cells_data.keys():
                    random_current = round(random.uniform(0, 5), 2)
                    monitor.update_cell_current(cell_id, random_current)
                st.rerun()
    
    # Main content area
    if not st.session_state.cells_data:
        st.info("👆 Add some battery cells using the sidebar to get started!")
        
        # Quick start section
        st.subheader("🚀 Quick Start")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Add LFP Cell", key="quick_lfp"):
                monitor.add_cell("lfp")
                st.rerun()
        
        with col2:
            if st.button("Add Li-ion Cell", key="quick_liion"):
                monitor.add_cell("li-ion")
                st.rerun()
        
        with col3:
            if st.button("Add 3 Random Cells", key="quick_random"):
                for _ in range(3):
                    cell_type = random.choice(monitor.valid_cell_types)
                    success, _ = monitor.add_cell(cell_type)
                    if not success:
                        break
                st.rerun()
    else:
        # Display current status
        df = monitor.get_cells_dataframe()
        
        # Metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Cells", len(df))
        
        with col2:
            active_cells = len(df[df['status'] == 'Active'])
            st.metric("Active Cells", active_cells)
        
        with col3:
            total_capacity = df['capacity'].sum()
            st.metric("Total Capacity", f"{total_capacity:.2f} Wh")
        
        with col4:
            avg_temp = df['temp'].mean()
            st.metric("Avg Temperature", f"{avg_temp:.1f}°C")
        
        with col5:
            total_current = df['current'].sum()
            st.metric("Total Current", f"{total_current:.2f} A")
        
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Cell Status", "⚡ Update Currents", "📈 Analytics", "💾 Export"])
        
        with tab1:
            st.subheader("Current Cell Status")
            
            # Display table with styling
            styled_df = df.copy()
            styled_df = styled_df.drop(['created'], axis=1, errors='ignore')
            
            # Color code status
            def highlight_status(val):
                if val == 'Active':
                    return 'background-color: #d4edda; color: #155724'
                elif val == 'Standby':
                    return 'background-color: #fff3cd; color: #856404'
                else:
                    return 'background-color: #f8f9fa; color: #6c757d'
            
            st.dataframe(
                styled_df.style.applymap(highlight_status, subset=['status']),
                use_container_width=True
            )
            
            # Individual cell removal
            st.subheader("🗑️ Remove Individual Cells")
            if len(df) > 0:
                cell_to_remove = st.selectbox(
                    "Select cell to remove",
                    df['Cell ID'].tolist()
                )
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("Remove Cell", type="secondary"):
                        success, message = monitor.remove_cell(cell_to_remove)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                        st.rerun()
        
        with tab2:
            st.subheader("⚡ Update Cell Currents")
            
            # Create form for updating currents
            with st.form("update_currents"):
                st.write("Update current values for each cell:")
                
                updated_currents = {}
                for _, row in df.iterrows():
                    cell_id = row['Cell ID']
                    current_value = row['current']
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{cell_id}** ({row['type'].upper()})")
                    with col2:
                        new_current = st.number_input(
                            f"Current (A)",
                            value=float(current_value),
                            min_value=0.0,
                            max_value=10.0,
                            step=0.1,
                            key=f"current_{cell_id}"
                        )
                        updated_currents[cell_id] = new_current
                    with col3:
                        capacity = row['voltage'] * new_current
                        st.write(f"→ {capacity:.2f} Wh")
                
                submitted = st.form_submit_button("🔄 Update All Currents", type="primary")
                
                if submitted:
                    for cell_id, current in updated_currents.items():
                        monitor.update_cell_current(cell_id, current)
                    st.success("✅ All currents updated successfully!")
                    st.rerun()
        
        with tab3:
            st.subheader("📈 Analytics & Visualizations")
            
            if len(df) > 0:
                # Charts row
                col1, col2 = st.columns(2)
                
                with col1:
                    # Capacity by cell type
                    capacity_by_type = df.groupby('type')['capacity'].sum().reset_index()
                    fig1 = px.pie(
                        capacity_by_type, 
                        values='capacity', 
                        names='type',
                        title='Capacity Distribution by Cell Type'
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Current vs Voltage scatter
                    fig2 = px.scatter(
                        df,
                        x='voltage',
                        y='current',
                        size='capacity',
                        color='type',
                        title='Current vs Voltage (Size = Capacity)',
                        hover_data=['Cell ID', 'temp', 'status']
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Temperature distribution
                fig3 = px.histogram(
                    df,
                    x='temp',
                    color='type',
                    title='Temperature Distribution',
                    nbins=10
                )
                st.plotly_chart(fig3, use_container_width=True)
                
                # Status summary
                status_counts = df['status'].value_counts()
                fig4 = px.bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    title='Cell Status Summary',
                    color=status_counts.index
                )
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("No data available for analytics")
        
        with tab4:
            st.subheader("💾 Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Export as JSON**")
                json_data = monitor.export_data('json')
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"battery_cells_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                with st.expander("Preview JSON"):
                    st.code(json_data, language='json')
            
            with col2:
                st.write("**Export as CSV**")
                csv_data = monitor.export_data('csv')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"battery_cells_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                with st.expander("Preview CSV"):
                    st.dataframe(df)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            🔋 Battery Cell Status Monitor | Built with Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
