from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem, Draw, rdFMCS
from rdkit.Chem.AtomPairs import Pairs
from rdkit.Chem.Fingerprints import FingerprintMols
import matplotlib.pyplot as plt
import pandas as pd
import requests
import statsmodels as sm
import time
from PIL import Image
from base64 import b64decode
from io import StringIO
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score, KFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from lazypredict.Supervised import LazyClassifier
from mordred import Calculator, descriptors, WienerIndex, ZagrebIndex
import param

def intro():
    description = """ChemLigandSeek is a Python package designed to facilitate ligand-based drug discovery tasks. 
    It provides functions for analyzing chemical compounds, predicting active compounds, and comparing QSAR machine learning algorithms.

    Functions available in ChemLigandSeek:

    1. display_active_chemicals_by_assay_aid(assay_aid):
        - Retrieves and displays active chemicals based on a given assay AID.

    2. display_inactive_chemicals_by_assay_aid(assay_aid):
        - Retrieves and displays inactive chemicals based on a given assay AID.

    3. predict_candidate_active_chemicals(assay_aid):
        - Predicts candidate active chemicals for a given assay AID.

    4. bioassay_pubchem_qsar_ml_algorithm_comparison(top_n):
        - Compares QSAR machine learning algorithms based on PubChem bioassay data.

    5. virtual_screening(csv_file):
        - Predicts candidate active chemicals from a CSV file containing SMILES strings of compounds.
          This function performs similarity search, filtering, and draws structures of the top candidates.

    """
    print(description)
intro()
################################################################################################################



def display_active_chemicals_by_assay_aid(aid):
    """
    Retrieves inactive compound CIDs from a specified assay and displays the common substructure.

    Parameters:
    - aid (int): Assay ID.

    Returns:
    - str: URL of the inactive compound CID data.
    """

    study_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/cids/txt?cids_type=active"
    url = requests.get(study_url)
    cids = url.text.split()
    str_cid = ",".join(str(x) for x in cids)

    compound_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{str_cid}/property/IsomericSMILES/txt"
    res = requests.get(compound_url)
    ms = res.text.split()
    molecules = list(map(Chem.MolFromSmiles, ms))
    grid_image = Chem.Draw.MolsToGridImage(molecules, subImgSize=(400, 400))
    display(grid_image)

    mcs_result = rdFMCS.FindMCS(molecules, threshold=0.7)
    common_substructure = Chem.MolFromSmarts(mcs_result.smartsString)

    print("The common substructure for these CIDs:")
    display(common_substructure)
    return compound_url

#display_active_chemicals_by_assay_aid(1000)


####################################################################

def display_inactive_chemicals_by_assay_aid(aid):
    """
    Retrieves inactive compound CIDs from a specified assay and displays the common substructure.

    Parameters:
    - aid (int): Assay ID.

    Returns:
    - str: URL of the inactive compound CID data.
    """

    study_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/cids/txt?cids_type=inactive"
    url = requests.get(study_url)
    cids = url.text.split()
    str_cid = ",".join(str(x) for x in cids)

    compound_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{str_cid}/property/IsomericSMILES/txt"
    res = requests.get(compound_url)
    ms = res.text.split()
    molecules = list(map(Chem.MolFromSmiles, ms))
    grid_image = Chem.Draw.MolsToGridImage(molecules, subImgSize=(400, 400))
    display(grid_image)

    mcs_result = rdFMCS.FindMCS(molecules, threshold=0.7)
    common_substructure = Chem.MolFromSmarts(mcs_result.smartsString)

    print("The common substructure for these CIDs:")
    display(common_substructure)
    return compound_url
#display_inactive_chemicals_by_assay_aid(1000)
###############################################################################################################################

import requests
import pandas as pd
import time
from io import StringIO
from rdkit import Chem
from rdkit.Chem import Draw

def ligand_based_screening(assay_id):
    # Step 1: Retrieve CIDs from the first link
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{assay_id}/cids/txt?cids_type=active"
    cid_response = requests.get(cid_url)
    cid_list = cid_response.text.split()

    # Step 2: Loop over CIDs to retrieve SMILES
    data = []

    for cid in cid_list:
        smiles_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IsomericSMILES/txt"
        smiles_response = requests.get(smiles_url)
        smiles = smiles_response.text.strip()

        data.append({'CID': cid, 'IsomericSMILES': smiles})

    # Step 3: Save data to DataFrame and then to a CSV file
    df = pd.DataFrame(data)
    df.to_csv(f"output_{assay_id}.csv", index=False)

    # Step 4: Perform similarity search
    prolog = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    cids_hit = dict()

    for idx, mysmiles in enumerate(df['IsomericSMILES']):
        mydata = {'smiles': mysmiles}
        url = prolog + "/compound/fastsimilarity_2d/smiles/cids/txt"
        res = requests.post(url, data=mydata)

        if res.status_code == 200:
            cids = res.text.split()
            cids = [int(x) for x in cids]    # Convert CIDs from string to integer.
        else:
            print("Error at", idx, ":", df.loc[idx, 'CID'], mysmiles)
            print(res.status_code)
            print(res.content)
            continue  # Skip to the next iteration if there's an error

        for mycid in cids:
            cids_hit[mycid] = cids_hit.get(mycid, 0) + 1

        time.sleep(0.2)


    # Step 5: Exclude query compounds from hits
    cids_query = dict()

    for idx, mysmiles in enumerate(df['IsomericSMILES']):
        mydata = {'smiles': mysmiles}
        url = prolog + "/compound/fastidentity/smiles/cids/txt?identity_type=same_connectivity"
        res = requests.post(url, data=mydata)

        if res.status_code == 200:
            cids = res.text.split()
            cids = [int(x) for x in cids]
        else:
            print("Error at", idx, ":", df.loc[idx, 'CID'], mysmiles)
            print(res.status_code)
            print(res.content)

        for mycid in cids:
            cids_query[mycid] = cids_query.get(mycid, 0) + 1

        time.sleep(0.2)

    # Step 6: Exclude query compounds from hits
    cids_hit = {k: v for k, v in cids_hit.items() if k not in cids_query}

    # Step 7: Filtering out non-drug-like compounds
    chunk_size = 100

    if len(cids_hit) % chunk_size == 0:
        num_chunks = len(cids_hit) // chunk_size
    else:
        num_chunks = len(cids_hit) // chunk_size + 1

    cids_list = list(cids_hit.keys())

    print("# Number of chunks:", num_chunks)

    csv = ""   # sets a variable called csv to save the comma-separated output

    for i in range(num_chunks):
        print(i, end=" ")

        idx1 = chunk_size * i
        idx2 = chunk_size * (i + 1)

        cids_str = ",".join([str(x) for x in cids_list[idx1:idx2]])  # build pug input for chunks of data
        url = prolog + f"/compound/cid/{cids_str}/property/HBondDonorCount,HBondAcceptorCount,MolecularWeight,XLogP,CanonicalSMILES,IsomericSMILES/csv"

        res = requests.get(url)

        if i == 0:  # if this is the first request, store result in an empty csv variable
            csv = res.text
        else:          # if this is a subsequent request, add the request to the csv variable adding a new line between chunks
            csv = csv + "\n".join(res.text.split()[1:]) + "\n"

        time.sleep(0.2)

    # Step 8: Downloaded data (in CSV) are loaded into a pandas data frame
    csv_file = StringIO(csv)
    df_raw = pd.read_csv(csv_file, sep=",")

    # Step 9: Show the shape (dimensions) of the data frame
    print("DataFrame Shape:", df_raw.shape)

    # Step 10: First load the cids_hit dictionary into a data frame
    df_freq = pd.DataFrame(cids_hit.items(), columns=['CID', 'HitFreq'])
    df_freq.head(5)

    # Step 11: Create a new data frame called "df" by joining the df and df_freq data frames
    df = df_raw.join(df_freq.set_index('CID'), on='CID')
    df.shape
    df.sort_values(by=['HitFreq', 'CID'], ascending=False).head(10)

    # Step 12: Filter out non-drug-like compounds
    df = df[(df['HBondDonorCount'] <= 5) &
            (df['HBondAcceptorCount'] <= 10) &
            (df['MolecularWeight'] <= 500) &
            (df['XLogP'] < 5)]

    # Step 13: Draw the structures of the top 10 compounds
    cids_top = df.sort_values(by=['HitFreq', 'CID'], ascending=False).head(10).CID.to_list()
    # Save the original DataFrame to a CSV file
    df.to_csv(f'Prediction candiate active chemical for with filter out non_drug{assay_id}.csv', index=False)

    mols = []

    for mycid in cids_top:
        mysmiles = df[df.CID == mycid].IsomericSMILES.item()
        mol = Chem.MolFromSmiles(mysmiles)
        Chem.FindPotentialStereoBonds(mol)  # Identify potential stereo bonds!
        mols.append(mol)

    mylegends = ["CID " + str(x) for x in cids_top]
    img = Draw.MolsToGridImage(mols, molsPerRow=2, subImgSize=(400, 400), legends=mylegends)
    display(img)
    # Save the image to a PNG file
    fil=str(f'Prediction candiate active chemical is saved Prediction candiate active chemical for with filter out non_drug{assay_id}.csv')
    print(fil)
    return
#ligand_based_screening(1000)


########################################################################################################
def ligand_based_screening_rule_of_3(assay_id):
    # Step 1: Retrieve CIDs from the first link
    cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{assay_id}/cids/txt?cids_type=active"
    cid_response = requests.get(cid_url)
    cid_list = cid_response.text.split()

    # Step 2: Loop over CIDs to retrieve SMILES
    data = []

    for cid in cid_list:
        smiles_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IsomericSMILES/txt"
        smiles_response = requests.get(smiles_url)
        smiles = smiles_response.text.strip()

        data.append({'CID': cid, 'IsomericSMILES': smiles})

    # Step 3: Save data to DataFrame and then to a CSV file
    df = pd.DataFrame(data)
    df.to_csv(f"output_{assay_id}.csv", index=False)

    # Step 4: Perform similarity search
    prolog = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    cids_hit = dict()

    for idx, mysmiles in enumerate(df['IsomericSMILES']):
        mydata = {'smiles': mysmiles}
        url = prolog + "/compound/fastsimilarity_2d/smiles/cids/txt"
        res = requests.post(url, data=mydata)

        if res.status_code == 200:
            cids = res.text.split()
            cids = [int(x) for x in cids]    # Convert CIDs from string to integer.
        else:
            print("Error at", idx, ":", df.loc[idx, 'CID'], mysmiles)
            print(res.status_code)
            print(res.content)
            continue  # Skip to the next iteration if there's an error

        for mycid in cids:
            cids_hit[mycid] = cids_hit.get(mycid, 0) + 1

        time.sleep(0.2)


    # Step 5: Exclude query compounds from hits
    cids_query = dict()

    for idx, mysmiles in enumerate(df['IsomericSMILES']):
        mydata = {'smiles': mysmiles}
        url = prolog + "/compound/fastidentity/smiles/cids/txt?identity_type=same_connectivity"
        res = requests.post(url, data=mydata)

        if res.status_code == 200:
            cids = res.text.split()
            cids = [int(x) for x in cids]
        else:
            print("Error at", idx, ":", df.loc[idx, 'CID'], mysmiles)
            print(res.status_code)
            print(res.content)

        for mycid in cids:
            cids_query[mycid] = cids_query.get(mycid, 0) + 1

        time.sleep(0.2)

    # Step 6: Exclude query compounds from hits
    cids_hit = {k: v for k, v in cids_hit.items() if k not in cids_query}

    # Step 7: Filtering out non-drug-like compounds
    chunk_size = 100

    if len(cids_hit) % chunk_size == 0:
        num_chunks = len(cids_hit) // chunk_size
    else:
        num_chunks = len(cids_hit) // chunk_size + 1

    cids_list = list(cids_hit.keys())

    print("# Number of chunks:", num_chunks)

    csv = ""   # sets a variable called csv to save the comma-separated output

    for i in range(num_chunks):
        print(i, end=" ")

        idx1 = chunk_size * i
        idx2 = chunk_size * (i + 1)

        cids_str = ",".join([str(x) for x in cids_list[idx1:idx2]])  # build pug input for chunks of data
        url = prolog + f"/compound/cid/{cids_str}/property/HBondDonorCount,HBondAcceptorCount,MolecularWeight,XLogP,CanonicalSMILES,IsomericSMILES/csv"

        res = requests.get(url)

        if i == 0:  # if this is the first request, store result in an empty csv variable
            csv = res.text
        else:          # if this is a subsequent request, add the request to the csv variable adding a new line between chunks
            csv = csv + "\n".join(res.text.split()[1:]) + "\n"

        time.sleep(0.2)

    # Step 8: Downloaded data (in CSV) are loaded into a pandas data frame
    csv_file = StringIO(csv)
    df_raw = pd.read_csv(csv_file, sep=",")

    # Step 9: Show the shape (dimensions) of the data frame
    print("DataFrame Shape:", df_raw.shape)

    # Step 10: First load the cids_hit dictionary into a data frame
    df_freq = pd.DataFrame(cids_hit.items(), columns=['CID', 'HitFreq'])
    df_freq.head(5)

    # Step 11: Create a new data frame called "df" by joining the df and df_freq data frames
    df = df_raw.join(df_freq.set_index('CID'), on='CID')
    df.shape
    df.sort_values(by=['HitFreq', 'CID'], ascending=False).head(10)

    # Step 12: Filter out compounds based on the Rule of Three and logP
    df = df[(df['HBondDonorCount'] <= 3) &
            (df['HBondAcceptorCount'] <= 3) &
            (df['MolecularWeight'] <= 300) &
            (df['XLogP'] < 3)]
    # Step 13: Draw the structures of the top 10 compounds
    cids_top = df.sort_values(by=['HitFreq', 'CID'], ascending=False).head(10).CID.to_list()
    # Save the original DataFrame to a CSV file
    df.to_csv(f'Prediction candiate active chemical for with filter out non_drug{assay_id}.csv', index=False)

    mols = []

    for mycid in cids_top:
        mysmiles = df[df.CID == mycid].IsomericSMILES.item()
        mol = Chem.MolFromSmiles(mysmiles)
        Chem.FindPotentialStereoBonds(mol)  # Identify potential stereo bonds!
        mols.append(mol)

    mylegends = ["CID " + str(x) for x in cids_top]
    img = Draw.MolsToGridImage(mols, molsPerRow=2, subImgSize=(400, 400), legends=mylegends)
    display(img)
    # Save the image to a PNG file
    fil=str(f'Prediction candiate active chemical is saved Prediction candiate active chemical for with filter out non_drug{assay_id}.csv')
    print(fil)
    return
#ligand_based_screening_rule_of_3(1000)

########################################################################################################################################

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from base64 import b64decode
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import confusion_matrix, classification_report
from lazypredict.Supervised import LazyClassifier

def PCFP_BitString(pcfp_base64):
    pcfp_bitstring = "".join(["{:08b}".format(x) for x in b64decode(pcfp_base64)])[32:913]
    return pcfp_bitstring

def get_target_values_meanings(y):
    unique_values = y.unique()
    meanings = {val: val for val in unique_values}
    return meanings

def bioassay_pubchem_qsar_ml_algorithm_comparison(aid_input):
    def retrieve_active_inactive_cids_with_fingerprints_and_pcfp(aid):
        url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/cids/txt?cids_type=active'

        # Fetch active CIDs
        response = requests.get(url)
        active_cids = set(map(int, response.text.strip().split()))

        # Create DataFrame
        df1 = pd.DataFrame(list(active_cids), columns=['CID'])
        df1['Activity'] = 'Active'
        url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/cids/txt?cids_type=inactive'

        # Fetch inactive CIDs
        response = requests.get(url)
        inactive_cids = set(map(int, response.text.strip().split()))

        # Create DataFrame
        df2 = pd.DataFrame(list(inactive_cids), columns=['CID'])
        df2['Activity'] = 'Inactive'
        # Combine df1 and df2 into a single DataFrame
        df = pd.concat([df1, df2], ignore_index=True)

        # Retrieve fingerprints and PCFP for each CID
        for cid in df['CID']:
            fingerprint_url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Fingerprint2D/txt'
            fingerprint_response = requests.get(fingerprint_url)
            fingerprint = fingerprint_response.text.strip()

            # Add fingerprint to the DataFrame
            df.loc[df['CID'] == cid, 'Fingerprint2D'] = fingerprint

            # Decode base64 fingerprint and extract PCFP bitstring
            pcfp_bitstring = PCFP_BitString(fingerprint)

            # Add PCFP bitstring columns to the DataFrame
            pcfp_columns = [f'PubchemFP{i}' for i in range(len(pcfp_bitstring))]
            df.loc[df['CID'] == cid, pcfp_columns] = list(pcfp_bitstring)

        return df

    result_df = retrieve_active_inactive_cids_with_fingerprints_and_pcfp(aid_input)
    result_df = result_df.drop(['CID', 'Fingerprint2D'], axis=1)

    # Store unique values of the 'Activity' column before encoding
    unique_activities = result_df['Activity'].unique().tolist()

    # Encode the 'Activity' column based on the unique values
    activity_encoding = {activity: idx for idx, activity in enumerate(unique_activities)}
    result_df['Activity'] = result_df['Activity'].map(activity_encoding)

    # Convert result_df to integers
    result_df = result_df.astype(int)

    # Display the modified DataFrame
    display(result_df)

    # Separate features and target
    X = result_df.drop('Activity', axis=1)
    y = result_df['Activity']

    # Store target meanings as unique activities
    target_meanings = get_target_values_meanings(y)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(result_df.drop('Activity', axis=1), result_df['Activity'], test_size=0.2, random_state=2)

    # LazyClassifier
    clf = LazyClassifier(verbose=0, ignore_warnings=True, custom_metric=None, predictions=True)
    models, _ = clf.fit(X_train, X_test, y_train, y_test)

    # Plot the model accuracies
    plt.figure(figsize=(5, 10))
    sns.set_theme(style="whitegrid")
    ax = sns.barplot(y=models.index, x="Accuracy", data=models, palette='viridis')
    ax.set(xlim=(0, 1))
    plt.show()

    # RandomForestClassifier
    clf_rf = RandomForestClassifier(n_estimators=500, random_state=1)
    clf_rf.fit(X_train, y_train)
    y_pred_class_rf = clf_rf.predict(X_test)

    # XGBClassifier
    xgbc = XGBClassifier()
    xgbc.fit(X_train, y_train)
    y_pred_class_xgb = xgbc.predict(X_test)

    # Cross-validation scores
    scores_rf = cross_val_score(clf_rf, X_train, y_train, cv=5)
    print("Random Forest Mean cross-validation score: %.2f" % scores_rf.mean())

    kfold = KFold(n_splits=10, shuffle=True)
    kf_cv_scores_xgb = cross_val_score(xgbc, X_train, y_train, cv=kfold)
    print("XGBClassifier K-fold CV average score: %.2f" % kf_cv_scores_xgb.mean())

    # Feature Importance with Random Forest
    importance_rf = clf_rf.feature_importances_
    feature_names = X.columns
    fp_rf = sorted(range(len(importance_rf)), key=lambda i: importance_rf[i], reverse=True)[:20]
    imp_values_rf = sorted(importance_rf, reverse=True)[:20]

    feature_names_rf = [feature_names[i] for i in fp_rf]
    imp_values_rf

    fake_rf = pd.DataFrame({'ind': feature_names_rf, 'importance__': imp_values_rf})

    # Plot Feature Importance
    sns.set_color_codes("pastel")
    ax_rf = sns.barplot(x='ind', y='importance__', data=fake_rf)
    ax_rf.set(xlabel='Features', ylabel='importance')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

    clf = RandomForestClassifier(n_estimators=500, random_state=1)
    clf.fit(X_train, y_train)
    y_pred_class = clf.predict(X_test)

    # Reverse target encoding for confusion matrix labels
    reverse_activity_encoding = {v: k for k, v in activity_encoding.items()}
    y_test_mapped = y_test.map(reverse_activity_encoding)
    y_pred_class_mapped = pd.Series(y_pred_class).map(reverse_activity_encoding)

    cf_matrix = confusion_matrix(y_test_mapped, y_pred_class_mapped)

    # Plot confusion matrix with target values meanings as titles
    sns.heatmap(cf_matrix, annot=True, cmap='Blues', xticklabels=unique_activities, yticklabels=unique_activities)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.show()

    print(classification_report(y_test_mapped, y_pred_class_mapped))

# Example usage:
#bioassay_pubchem_qsar_ml_algorithm_comparison(1000)


################################################################################################


import pandas as pd
import requests
import time
from io import StringIO
from rdkit import Chem
from rdkit.Chem import Draw

def virtual_screening(csv_file, smiles_column):
    # Step 1: Read CSV file
    df_act = pd.read_csv(csv_file)
    smiles_act = df_act[smiles_column].tolist()

    # Step 2: Perform similarity search
    prolog = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    cids_hit = dict()

    for idx, mysmiles in enumerate(smiles_act):
        mydata = {'smiles': mysmiles}
        url = prolog + "/compound/fastsimilarity_2d/smiles/cids/txt"
        res = requests.post(url, data=mydata)

        if res.status_code == 200:
            cids = res.text.split()
            cids = [int(x) for x in cids]    # Convert CIDs from string to integer.
        else:
            print("Error at", idx, ":", idx, mysmiles)
            print(res.status_code)
            print(res.content)
            continue  # Skip to the next iteration if there's an error

        for mycid in cids:
            cids_hit[mycid] = cids_hit.get(mycid, 0) + 1

        time.sleep(0.2)

    # Step 3: Exclude query compounds from hits
    cids_query = dict()

    for idx, mysmiles in enumerate(smiles_act):
        mydata = {'smiles': mysmiles}
        url = prolog + "/compound/fastidentity/smiles/cids/txt?identity_type=same_connectivity"
        res = requests.post(url, data=mydata)

        if res.status_code == 200:
            cids = res.text.split()
            cids = [int(x) for x in cids]
        else:
            print("Error at", idx, ":", idx, mysmiles)
            print(res.status_code)
            print(res.content)

        for mycid in cids:
            cids_query[mycid] = cids_query.get(mycid, 0) + 1

        time.sleep(0.2)

    # Step 4: Exclude query compounds from hits
    cids_hit = {k: v for k, v in cids_hit.items() if k not in cids_query}

    # Step 5: Filtering out non-drug-like compounds
    chunk_size = 100

    if len(cids_hit) % chunk_size == 0:
        num_chunks = len(cids_hit) // chunk_size
    else:
        num_chunks = len(cids_hit) // chunk_size + 1

    cids_list = list(cids_hit.keys())

    print("# Number of chunks:", num_chunks)

    csv = ""   # sets a variable called csv to save the comma-separated output

    for i in range(num_chunks):
        print(i, end=" ")

        idx1 = chunk_size * i
        idx2 = chunk_size * (i + 1)

        cids_str = ",".join([str(x) for x in cids_list[idx1:idx2]])  # build pug input for chunks of data
        url = prolog + f"/compound/cid/{cids_str}/property/HBondDonorCount,HBondAcceptorCount,MolecularWeight,XLogP,CanonicalSMILES,IsomericSMILES/csv"

        res = requests.get(url)

        if i == 0:  # if this is the first request, store result in an empty csv variable
            csv = res.text
        else:          # if this is a subsequent request, add the request to the csv variable adding a new line between chunks
            csv = csv + "\n".join(res.text.split()[1:]) + "\n"

        time.sleep(0.2)

    # Step 6: Downloaded data (in CSV) are loaded into a pandas data frame
    csv_file = StringIO(csv)
    df_raw = pd.read_csv(csv_file, sep=",")

    # Step 7: Show the shape (dimensions) of the data frame
    print("DataFrame Shape:", df_raw.shape)

    # Step 8: First load the cids_hit dictionary into a data frame
    df_freq = pd.DataFrame(cids_hit.items(), columns=['CID', 'HitFreq'])
    df_freq.head(5)

    # Step 9: Create a new data frame called "df" by joining the df and df_freq data frames
    df = df_raw.join(df_freq.set_index('CID'), on='CID')
    df.shape
    df.sort_values(by=['HitFreq', 'CID'], ascending=False).head(10)

    # Step 10: Filter out compounds based on the Rule of Three and logP
    df = df[(df['HBondDonorCount'] <= 3) &
            (df['HBondAcceptorCount'] <= 3) &
            (df['MolecularWeight'] <= 300) &
            (df['XLogP'] < 3)]

    # Step 11: Draw the structures of the top 10 compounds
    cids_top = df.sort_values(by=['HitFreq', 'CID'], ascending=False).head(10).CID.to_list()

    mols = []

    for mycid in cids_top:
        mysmiles = df[df.CID == mycid].IsomericSMILES.item()
        mol = Chem.MolFromSmiles(mysmiles)
        Chem.FindPotentialStereoBonds(mol)  # Identify potential stereo bonds!
        mols.append(mol)

    mylegends = ["CID " + str(x) for x in cids_top]
    img = Draw.MolsToGridImage(mols, molsPerRow=2, subImgSize=(400, 400), legends=mylegends)
    display(img)
    # Save the image to a PNG file
    fil=str(f'Prediction candiate active chemical is saved Prediction candiate active chemical for with filter out non_drug{csv_file}.csv')
    print(fil)
    return

# Example usage:
#virtual_screening("AID_1107225_datatable_active.csv","'PUBCHEM_EXT_DATASOURCE_SMILES'")

#################################################################################################################################