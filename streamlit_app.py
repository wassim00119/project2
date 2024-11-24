import streamlit as st

# Functions
def create_vehicle(vehicle_id, make, model, year, fuel_level, efficiency, status="Available"):
    return {"ID": vehicle_id, "Make": make, "Model": model, "Year": year, "Fuel": fuel_level, "Efficiency": efficiency, "Status": status}

def create_shipment(shipment_id, origin, destination, status="Pending"):
    return {"ID": shipment_id, "Origin": origin, "Destination": destination, "Status": status, "Vehicle": None}

def create_route(start, end, distance):
    return {"Start": start, "End": end, "Distance": distance}

def create_warehouse(warehouse_id, location):
    return {"ID": warehouse_id, "Location": location, "Inventory": {}}

# Initialize session states
if "vehicles" not in st.session_state:
    st.session_state.vehicles = {}
if "shipments" not in st.session_state:
    st.session_state.shipments = {}
if "routes" not in st.session_state:
    st.session_state.routes = {}
if "warehouses" not in st.session_state:
    st.session_state.warehouses = {}

# Sidebar Menu
menu = st.sidebar.selectbox("Main Menu", ["Vehicles", "Shipments", "Routes", "Cost Estimation", "Warehouses"])

### Vehicles Section ###
if menu == "Vehicles":
    st.header("Vehicle Management")
    sub_menu = st.radio("Choose an action:", ["Add Vehicle", "View Vehicles", "Update Fuel", "Update Status"])

    if sub_menu == "Add Vehicle":
        st.subheader("Add a New Vehicle")
        vehicle_id = st.text_input("Vehicle ID")
        make = st.text_input("Make (Brand)")
        model = st.text_input("Model")
        year = st.text_input("Year")
        fuel_level = st.slider("Fuel Level", 0, 100, 50)
        efficiency = st.number_input("Efficiency (km/l)", min_value=0.1, value=10.0)
        if st.button("Add Vehicle"):
            if vehicle_id in st.session_state.vehicles:
                st.error("Vehicle ID already exists!")
            else:
                st.session_state.vehicles[vehicle_id] = create_vehicle(vehicle_id, make, model, year, fuel_level, efficiency)
                st.success("Vehicle added successfully!")

    elif sub_menu == "View Vehicles":
        st.subheader("All Vehicles")
        if st.session_state.vehicles:
            for v_id, vehicle in st.session_state.vehicles.items():
                st.write(f"*ID:* {vehicle['ID']}, *Make:* {vehicle['Make']}, *Model:* {vehicle['Model']}, "
                         f"*Year:* {vehicle['Year']}, *Fuel:* {vehicle['Fuel']}%, *Efficiency:* {vehicle['Efficiency']} km/l, "
                         f"*Status:* {vehicle['Status']}")
        else:
            st.info("No vehicles to display.")

    elif sub_menu == "Update Fuel":
        st.subheader("Update Vehicle Fuel")
        if st.session_state.vehicles:
            vehicle_id = st.selectbox("Select Vehicle ID", list(st.session_state.vehicles.keys()))
            fuel_change = st.slider("Fuel Change (negative to decrease)", -50, 50, 0)
            if st.button("Update Fuel"):
                vehicle = st.session_state.vehicles[vehicle_id]
                vehicle["Fuel"] = max(0, min(100, vehicle["Fuel"] + fuel_change))
                st.success(f"Fuel updated to {vehicle['Fuel']}% for Vehicle ID: {vehicle_id}")
        else:
            st.info("No vehicles available.")

    elif sub_menu == "Update Status":
        st.subheader("Update Vehicle Status")
        if st.session_state.vehicles:
            vehicle_id = st.selectbox("Select Vehicle ID", list(st.session_state.vehicles.keys()))
            status = st.selectbox("Select New Status", ["Available", "In Use", "Maintenance"])
            if st.button("Update Status"):
                vehicle = st.session_state.vehicles[vehicle_id]
                vehicle["Status"] = status
                st.success(f"Status updated to {status} for Vehicle ID: {vehicle_id}")
        else:
            st.info("No vehicles available.")

### Shipments Section ###
elif menu == "Shipments":
    st.header("Shipment Management")
    sub_menu = st.radio(
        "Choose an action:", 
        ["Add Shipment", "Assign Vehicle", "View Shipments", "Update Shipment Status"]
    )

    if sub_menu == "Add Shipment":
        st.subheader("Add a New Shipment")
        shipment_id = st.text_input("Shipment ID")
        origin = st.text_input("Origin")
        destination = st.text_input("Destination")
        if st.button("Add Shipment"):
            if shipment_id in st.session_state.shipments:
                st.error("Shipment ID already exists!")
            else:
                st.session_state.shipments[shipment_id] = create_shipment(shipment_id, origin, destination)
                st.success("Shipment added successfully!")

    elif sub_menu == "Assign Vehicle":
        st.subheader("Assign a Vehicle to Shipment")
        if st.session_state.shipments and st.session_state.vehicles:
            shipment_id = st.selectbox("Select Shipment ID", list(st.session_state.shipments.keys()))
            vehicle_id = st.selectbox("Select Vehicle ID", list(st.session_state.vehicles.keys()))
            if st.button("Assign Vehicle"):
                shipment = st.session_state.shipments[shipment_id]
                vehicle = st.session_state.vehicles[vehicle_id]
                if shipment["Vehicle"]:
                    st.warning("This shipment already has a vehicle assigned.")
                elif vehicle["Status"] == "In Use":
                    st.error("Vehicle is already in use!")
                else:
                    assign_vehicle_to_shipment(shipment, vehicle)
                    st.success(f"Vehicle {vehicle_id} assigned to shipment {shipment_id}.")
        else:
            st.info("No shipments or vehicles available for assignment.")

    elif sub_menu == "View Shipments":
        st.subheader("All Shipments")
        if st.session_state.shipments:
            for s_id, shipment in st.session_state.shipments.items():
                st.write(f"*ID:* {shipment['ID']}, *Origin:* {shipment['Origin']}, *Destination:* {shipment['Destination']}")
                st.write(f"*Status:* {shipment['Status']}, *Vehicle:* {shipment['Vehicle'] or 'Not Assigned'}")
        else:
            st.info("No shipments to display.")

    elif sub_menu == "Update Shipment Status":
        st.subheader("Update Shipment Status")
        if st.session_state.shipments:
            shipment_id = st.selectbox("Select Shipment ID", list(st.session_state.shipments.keys()))
            new_status = st.text_input("Enter New Status (e.g., Pending, In Transit, Delivered)")
            if st.button("Update Status"):
                shipment = st.session_state.shipments[shipment_id]
                shipment["Status"] = new_status
                st.success(f"Shipment {shipment_id} status updated to: {new_status}")
        else:
            st.info("No shipments available.")

### Routes Section ###
elif menu == "Routes":
    st.header("Route Management")
    sub_menu = st.radio("Choose an action:", ["Add Route", "View Routes"])

    if sub_menu == "Add Route":
        st.subheader("Add a New Route")
        start = st.text_input("Start Location")
        end = st.text_input("End Location")
        distance = st.number_input("Distance (in km)", min_value=1.0, value=10.0)
        if st.button("Add Route"):
            route_key = (start, end)
            if route_key in st.session_state.routes:
                st.error("Route already exists!")
            else:
                st.session_state.routes[route_key] = create_route(start, end, distance)
                st.success("Route added successfully!")

    elif sub_menu == "View Routes":
        st.subheader("All Routes")
        if st.session_state.routes:
            for (start, end), route in st.session_state.routes.items():
                st.write(f"*Start:* {route['Start']}, *End:* {route['End']}, *Distance:* {route['Distance']} km")
        else:
            st.info("No routes to display.")

### Cost Estimation Section ###
elif menu == "Cost Estimation":
    st.header("Estimate Delivery Costs")
    if st.session_state.vehicles and st.session_state.routes:
        vehicle_id = st.selectbox("Select Vehicle ID", list(st.session_state.vehicles.keys()))
        route_key = st.selectbox("Select Route", list(st.session_state.routes.keys()))
        fuel_price = st.number_input("Fuel Price per Liter", min_value=1.0, value=100.0)
        delivery_rate = st.number_input("Delivery Rate per km", min_value=1.0, value=10.0)

        if st.button("Estimate Costs"):
            vehicle = st.session_state.vehicles[vehicle_id]
            route = st.session_state.routes[route_key]
            fuel_cost = (route["Distance"] / vehicle["Efficiency"]) * fuel_price
            delivery_cost = route["Distance"] * delivery_rate
            total_cost = fuel_cost + delivery_cost
            st.write(f"*Fuel Cost:* {fuel_cost:.2f} units")
            st.write(f"*Delivery Cost:* {delivery_cost:.2f} units")
            st.write(f"*Total Cost:* {total_cost:.2f} units")
    else:
        st.info("No vehicles or routes available.")
elif menu == "Warehouses":
    st.header("Warehouse Management")
    sub_menu = st.radio(
        "Choose an action:", 
        ["Add Warehouse", "Manage Inventory", "View Warehouses", "Update Warehouse Status"]
    )

    if sub_menu == "Add Warehouse":
        st.subheader("Add a New Warehouse")
        warehouse_id = st.text_input("Warehouse ID")
        location = st.text_input("Location")
        if st.button("Add Warehouse"):
            if warehouse_id in st.session_state.warehouses:
                st.error("Warehouse ID already exists!")
            else:
                st.session_state.warehouses[warehouse_id] = create_warehouse(warehouse_id, location)
                st.success("Warehouse added successfully!")

    elif sub_menu == "Manage Inventory":
        st.subheader("Manage Warehouse Inventory")
        if st.session_state.warehouses:
            warehouse_id = st.selectbox("Select Warehouse ID", list(st.session_state.warehouses.keys()))
            warehouse = st.session_state.warehouses[warehouse_id]

            inventory_action = st.radio("Choose an action:", ["Add Stock", "Remove Stock"])
            item = st.text_input("Item Name")
            quantity = st.number_input("Quantity", min_value=1, step=1)

            if inventory_action == "Add Stock" and st.button("Add Stock"):
                if item in warehouse["Inventory"]:
                    warehouse["Inventory"][item] += quantity
                else:
                    warehouse["Inventory"][item] = quantity
                st.success(f"Added {quantity} units of {item} to Warehouse {warehouse_id}.")

            elif inventory_action == "Remove Stock" and st.button("Remove Stock"):
                if item in warehouse["Inventory"] and warehouse["Inventory"][item] >= quantity:
                    warehouse["Inventory"][item] -= quantity
                    if warehouse["Inventory"][item] == 0:
                        del warehouse["Inventory"][item]
                    st.success(f"Removed {quantity} units of {item} from Warehouse {warehouse_id}.")
                else:
                    st.error(f"Not enough {item} in Warehouse {warehouse_id}.")
        else:
            st.info("No warehouses available.")

    elif sub_menu == "View Warehouses":
    st.subheader("All Warehouses")
    if st.session_state.warehouses:
        for w_id, warehouse in st.session_state.warehouses.items():
            st.write(f"*ID:* {warehouse['ID']}, *Location:* {warehouse['Location']}, *Status:* {warehouse.get('Status', 'Not Set')}")
            st.write("*Inventory:*")
            if warehouse["Inventory"]:
                for item, qty in warehouse["Inventory"].items():
                    st.write(f"- {item}: {qty} units")
            else:
                st.write("- No inventory")
    else:
        st.info("No warehouses to display.")

    elif sub_menu == "Update Warehouse Status":
        st.subheader("Update Warehouse Status")
        if st.session_state.warehouses:
            warehouse_id = st.selectbox("Select Warehouse ID", list(st.session_state.warehouses.keys()))
            new_status = st.text_input("Enter New Status (e.g., Active, Inactive, Under Maintenance)")
            if st.button("Update Status"):
                warehouse = st.session_state.warehouses[warehouse_id]
                warehouse["Status"] = new_status
                st.success(f"Warehouse {warehouse_id} status updated to: {new_status}")
        else:
            st.info("No warehouses available.")
