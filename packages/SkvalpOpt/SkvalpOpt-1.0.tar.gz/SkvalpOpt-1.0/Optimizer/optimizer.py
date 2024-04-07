
#----------------------------------------------
# Import libraries
#----------------------------------------------
import pyomo.environ as pe
import pyomo.opt as po


#----------------------------------------------
# Define optimizer class
#----------------------------------------------

class SolarBessMPC:
    
    #----------------------------------------------
    # Constructor
    #----------------------------------------------
    def __init__(self, bess_pmax, bess_pmin, bess_soc_max, bess_soc_min, efficiency=1, dt=5/60) -> None:

        self.model = None
        # Define model parameters
        self.battery_upper_power_limit = bess_pmax
        self.battery_lower_power_limit = bess_pmin
        self.battery_energy_upper_limit = bess_soc_max
        self.battery_energy_lower_limit = bess_soc_min
        self.dt = dt
        self.efficiency = efficiency  # round trip efficiency

        # Initialize data
        self.price_data = None
        self.solar_data = None

        # Initialize model variables
        self.E_b_0_initialize = 0
        self.P_b_initialize = 0
        self.E_b_initialize = 0
        self.E_b_dch_initialize = 0
        self.E_b_ch_initialize = 0

    #----------------------------------------------
    # Define model
    #----------------------------------------------
    def create_model(self):
        self.model = pe.ConcreteModel()

    #----------------------------------------------
    # Define Horizon
    #----------------------------------------------
    def initialize_horizon(self, price_data, solar_data):

        self.solar_data = solar_data
        self.price_data = price_data
        self.model.horizon = pe.RangeSet(0, len(self.price_data) - 1)

    
    #----------------------------------------------
    # Set Objective
    #----------------------------------------------
    def set_objective(self):
        objective_function = sum((self.model.E_solar[t] + self.model.E_b_dch[t] - self.model.E_b_ch[t]) * self.model.pi[t] for t in self.model.horizon)
        self.model.obj_func = pe.Objective(sense=pe.maximize, expr=objective_function)

    #----------------------------------------------
    # Define rules
    #----------------------------------------------
    def rule_pi(self, model, t) -> float:
        return self.price_data[t]
    
    def rule_solar(self, model, t) -> float:
        return self.solar_data[t]
        
    def rule_battery_lower_power_limit(self, model, t):
        return self.model.P_b[t] >= self.battery_lower_power_limit
    
    def rule_battery_upper_power_limit(self, model, t):
        return self.model.P_b[t] <= self.battery_upper_power_limit
        
    def rule_battery_energy_upper_limit(self, model, t):
        return self.model.E_b[t] <= self.battery_energy_upper_limit
    
    def rule_battery_energy_lower_limit(self, model, t):
        return self.model.E_b[t] >= self.battery_energy_lower_limit
    
    def rule_energy_power_conversion(self, model, t):
        return self.model.P_b[t] == (self.model.E_b_dch[t] - self.model.E_b_ch[t]) / self.dt
    
    def rule_soc_update(self, model, t):
        if t == 0:
            return self.model.E_b[t] == (self.E_b_0_initialize - (self.model.E_b_dch[t] / self.efficiency) + (self.model.E_b_ch[t] * self.efficiency))
        return self.model.E_b[t] == (self.model.E_b[t - 1] - (self.model.E_b_dch[t] / self.efficiency) + (self.model.E_b_ch[t] * self.efficiency))

    #----------------------------------------------
    # Define constraints
    #----------------------------------------------
    def set_constraints(self):

        self.model.battery_lower_power_limit = pe.Constraint(self.model.horizon, rule=self.rule_battery_lower_power_limit)
        self.model.battery_upper_power_limit = pe.Constraint(self.model.horizon, rule=self.rule_battery_upper_power_limit)

        self.model.battery_energy_upper_limit = pe.Constraint(self.model.horizon, rule=self.rule_battery_energy_upper_limit)
        self.model.battery_energy_lower_limit = pe.Constraint(self.model.horizon, rule=self.rule_battery_energy_lower_limit)

        self.model.energy_power_conversion = pe.Constraint(self.model.horizon, rule=self.rule_energy_power_conversion)
        self.model.soc_update = pe.Constraint(self.model.horizon, rule=self.rule_soc_update)

        self.model.pi = pe.Param(self.model.horizon, initialize=self.rule_pi)
        self.model.E_solar = pe.Param(self.model.horizon, initialize=self.rule_solar)

        self.model.charge_discharge_sos = pe.SOSConstraint( var=[self.model.E_b_ch, self.model.E_b_dch], sos=1, index=pe.Set(self.model.horizon))

    #----------------------------------------------
    # Update model vars after each iteration
    #----------------------------------------------
    def update_model_variables(self):
        self.E_b_0_initialize = self.model.E_b[0].value
        self.P_b_initialize = list(self.model.P_b.extract_values().values())
        self.E_b_initialize = [max(eb, 0) for eb in list(self.model.E_b.extract_values().values())]
        self.E_b_dch_initialize = [max(eb_dch, 0) for eb_dch in list(self.model.E_b_dch.extract_values().values())]
        self.E_b_ch_initialize = [max(eb_ch, 0) for eb_ch in list(self.model.E_b_ch.extract_values().values())]

    #----------------------------------------------
    # Define variables
    #----------------------------------------------
    def define_model_variables(self):
        self.model.add_component('P_b', pe.Var(self.model.horizon, domain=pe.Reals, initialize=self.P_b_initialize))
        self.model.add_component('E_b', pe.Var(self.model.horizon, domain=pe.NonNegativeReals, initialize=self.E_b_initialize))
        self.model.add_component('E_b_dch', pe.Var(self.model.horizon, domain=pe.NonNegativeReals, initialize=self.E_b_dch_initialize))
        self.model.add_component('E_b_ch', pe.Var(self.model.horizon, domain=pe.NonNegativeReals, initialize=self.E_b_ch_initialize))
    
    #----------------------------------------------
    # Solve model
    #----------------------------------------------
    def solve_model(self, solver_name):
        solver = po.SolverFactory(solver_name)
        result = solver.solve(self.model, tee=False)
        return result

    #----------------------------------------------
    # return solution
    #----------------------------------------------
    def return_solution(self):

        battery_soc = list(self.model.E_b.extract_values().values())
        battery_power = list(self.model.P_b.extract_values().values())
        bat_charge = list(self.model.E_b_ch.extract_values().values())
        bat_discharge = list(self.model.E_b_dch.extract_values().values())

        return bat_charge, bat_discharge, battery_power, battery_soc

    #----------------------------------------------
    # Optimize model
    #----------------------------------------------
    def optimize_model(self, price_data:list, solar_data:list, solver_name:str):

        self.create_model()
        self.initialize_horizon(price_data, solar_data)
        self.define_model_variables()
        self.set_constraints()
        self.set_objective()
        results = self.solve_model(solver_name)
        bat_charge, bat_discharge, battery_power, battery_soc = self.return_solution()  
        self.update_model_variables()
        
        return results, bat_charge, bat_discharge, battery_power, battery_soc




