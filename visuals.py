import pandas as pd
import numpy as np
from collections import deque
import matplotlib.pyplot as plt

pd.set_option('display.float_format', '{:,.0f}'.format)

data = pd.read_csv('Bank Data.csv',thousands=',')


""" Constructing the Maximum Entropy Network """

def create_max_entropy_network(LAvector,VFvector,banks,tolerance=1e-4):
   
    n = len(banks)

    LAarray = np.array(LAvector, dtype=float)
    VFarray = np.array(VFvector, dtype=float)

    # Must ensure within this environment, total assets equals total liabilities. If not (which is likely), rescale

    LAtotal = np.sum(LAarray)
    VFtotal = np.sum(VFarray)

    if LAtotal != VFtotal:
        scaling_factor = min(LAtotal,VFtotal) / max(LAtotal,VFtotal)

        if LAtotal > VFtotal:
            LAarray = LAarray * scaling_factor
        else:
            VFarray = VFarray * scaling_factor

    LAtotal = np.sum(LAarray)
    exposure_matrix = np.outer(LAarray, VFarray) / LAtotal

    # Now, ensure bank does not 'lend to itself'; iteratively rescale rows then columns to meet MaxEnt solution

    print(f"\n\nExposure Matrix (Before Diagonal Corrections):\n")
    print(pd.DataFrame(exposure_matrix, index=banks, columns=banks))
    print(f"\n")

    for i in range(n):
        exposure_matrix[i,i] = 0

    max_error = 1
    while max_error >= tolerance:
        for i in range(n):
            row_sum = exposure_matrix[i, :].sum()
            if row_sum > 0:
                exposure_matrix[i, :] *= (LAarray[i] / row_sum)
                
        for j in range(n):
            col_sum = exposure_matrix[:, j].sum()
            if col_sum > 0:
                exposure_matrix[:, j] *= (VFarray[j] / col_sum)
        
        current_row_sums = exposure_matrix.sum(axis=1)
        current_col_sums = exposure_matrix.sum(axis=0)
        
        max_row_error = np.max(np.abs(current_row_sums - LAarray))
        max_col_error = np.max(np.abs(current_col_sums - VFarray))
        max_error = max(max_row_error, max_col_error)
    
    return pd.DataFrame(exposure_matrix, index=banks, columns=banks)




""" Calculation of 3 Key Metrics """

data['Liquid Assets'] = data['Cash and due from banks'] + data['Security agree to be resold']
data['Volatile Funding'] = data['Trading liabilities'] + data['Derivative product liabilities']
data['Tangible Equity'] = data['Net tangible assets']

clean_data = data[['Bank','Year End','Liquid Assets','Volatile Funding','Tangible Equity']]
melted_data = clean_data.melt(id_vars=['Bank', 'Year End'],var_name='Metric',value_name='Value')



""" Sensitivity Analysis of Runoff Rate, Cascade Model """

banks = ['Barclays', 'HSBC', 'NatWest', "Lloyd's", 'Standard Chartered', 'Santander']
n = len(banks)

target_years = [2022, 2023, 2024, 2025] 
runoff_steps = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

for target_year in target_years:
    
    # Records list for future graphing use
    plot_records = []

    print(f"\n\n================ For the Year {target_year} ================\n")

    year_baseline = clean_data[clean_data['Year End'] == target_year].copy()

    year_baseline['Liquidity Buffer'] = year_baseline['Liquid Assets'] - year_baseline['Volatile Funding']
    
    # Creates display copy so we don't alter original data
    display_df = year_baseline.copy()
    display_df['Liquid Assets'] = display_df['Liquid Assets'] * 1000
    display_df['Volatile Funding'] = display_df['Volatile Funding'] * 1000
    display_df['Tangible Equity'] = display_df['Tangible Equity'] * 1000
    display_df['Initial Liquidity Buffer'] = display_df['Liquidity Buffer'] * 1000

    print("Baseline Balance Sheets:")
    print(display_df[['Bank', 'Liquid Assets', 'Volatile Funding', 'Tangible Equity', 'Initial Liquidity Buffer']].to_string(index=False))

    liability_matrix = create_max_entropy_network(year_baseline['Liquid Assets'], year_baseline['Volatile Funding'], banks)
    print(f"Liability Matrix (After Diagonal Corrections):\n")
    print(liability_matrix)

    # Set Runoff Rate, represents proportion of volatile funding that is pulled during a run
    for runoff in runoff_steps:

        print(f"\n----- Using runoff rate: {runoff} -----")

        year_data = year_baseline.copy()

        # Calculation of Liquidity Buffer, Checking for Breach
        year_data['Liquidity Buffer'] = year_data['Liquid Assets'] - year_data['Volatile Funding']
        year_data['Stressed Liquid Assets'] = year_data['Liquid Assets'] - runoff * year_data['Volatile Funding']
        year_data['Breached'] = year_data['Stressed Liquid Assets'] < 0

        initial_breached_banks = []
        cascade_queue = deque()

        for bank in banks:
            bank_row = year_data['Bank'] == bank

            is_breached_initially = year_data.loc[bank_row, 'Breached'].values[0]
            
            if is_breached_initially == True:
                initial_breached_banks.append(bank)
                cascade_queue.append(bank)

        while cascade_queue:
            bank_A = cascade_queue.popleft() 
            print(f"Impact of failure of {bank_A}:")

            others_green = False

            for other_bank in banks:
                other_bank_row = year_data['Bank'] == other_bank
                is_breached = year_data.loc[other_bank_row, 'Breached'].values[0]
                
                if is_breached == False:
                    others_green = True

                    loss = liability_matrix.loc[other_bank, bank_A]
                    
                    # Subtract loss directly from the other banks' current liquid assets
                    LAcurrent = year_data.loc[other_bank_row, 'Stressed Liquid Assets'].values[0]
                    LAnew = LAcurrent - loss
                    year_data.loc[other_bank_row, 'Stressed Liquid Assets'] = LAnew
                    
                    # Recalculate Liquidity Buffer
                    VFnew = year_data.loc[other_bank_row, 'Volatile Funding'].values[0]
                    remaining_liabilities = VFnew * (1 - runoff)
                    new_buffer = LAnew - remaining_liabilities

                    print(f"↳ Impact on {other_bank}:")
                    print(f"• Exposure to {bank_A}: £{loss * 1000:,.2f}")
                    print(f"• Stressed Assets:  £{LAcurrent * 1000:,.2f} is now £{LAnew * 1000:,.2f}")
                    print(f"• Remaining Buffer: £{new_buffer * 1000:,.2f}")
                    
                    # If new buffer < 0, join the failure queue, similar to BFS method
                    if new_buffer < 0:
                        year_data.loc[other_bank_row, 'Breached'] = True
                        
                        cascade_queue.append(other_bank)

            if not others_green:
                print('No surviving counterparties to continue cascade analysis.')

        initial_failures_count = len(initial_breached_banks)
        total_failures_count = int(year_data['Breached'].sum())
        
        # Applying each result to the records for graphing use
        plot_records.append({
            'Runoff Rate': runoff,
            'Initial Failures': initial_failures_count,
            'Total Failures': total_failures_count
        })

        # Text Observation
        final_failed_banks = year_data[year_data['Breached'] == True]['Bank'].tolist()
        surviving_banks = year_data[year_data['Breached'] == False]['Bank'].tolist()

        print(f"Initial Breaches: {initial_breached_banks}")
        print(f"Final Failed Banks: {final_failed_banks}")
        print(f"Surviving Banks: {surviving_banks}")
        print(f"Total Cascade Size: {len(final_failed_banks)}\n")

    # Convert arrays into a single dataframe for use in MatPlotLib
    sensitivity_df = pd.DataFrame(plot_records)

    plt.plot(sensitivity_df['Runoff Rate'], sensitivity_df['Initial Failures'], 
            marker='o', color="#000DFF", linewidth=2, label='Initial Failures')

    plt.plot(sensitivity_df['Runoff Rate'], sensitivity_df['Total Failures'], 
            marker='s', color="#FF0000", linewidth=2, linestyle='--', label='Total Failures (After Cascade)')

    plt.title(f'Liquidity Stress Sensitivity and Systemic Cascades ({target_year})')
    plt.xlabel('Runoff Rate (Proportion of Volatile Funding Withdrawn)')
    plt.ylabel('Number of Failed Banks (Out of 6)')

    plt.xticks(np.arange(0.1,1.1,0.1))
    plt.yticks(range(0,8))

    plt.grid(True,linestyle=':',color='gray')
    plt.legend(fontsize='small',loc='upper left',frameon=True,facecolor='white',edgecolor='none',shadow=False)
    plt.tight_layout()

    plt.savefig(f'sensitivity_{target_year}.png')
    plt.clf()