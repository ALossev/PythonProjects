import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix, 
                           roc_auc_score, roc_curve, precision_recall_curve)
from sklearn.feature_selection import SelectKBest, f_classif
import warnings
warnings.filterwarnings('ignore')

class EnhancedDataClassifier:
    def __init__(self, csv_file="customer_data.csv"):
        """Initialize the enhanced classifier with comprehensive functionality."""
        self.csv_file = csv_file
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.best_model = None
        self.scaler = StandardScaler()
        self.feature_selector = None
        
    def load_and_explore_data(self):
        """Load data and perform comprehensive exploratory data analysis."""
        print("=" * 50)
        print("LOADING AND EXPLORING DATA")
        print("=" * 50)
        
        # Load data
        self.df = pd.read_csv(self.csv_file)
        
        # Basic info
        print(f"Dataset shape: {self.df.shape}")
        print(f"\nData types:\n{self.df.dtypes}")
        print(f"\nMissing values:\n{self.df.isnull().sum()}")
        print(f"\nDataset preview:")
        print(self.df.head())
        
        # Statistical summary
        print(f"\nStatistical Summary:")
        print(self.df.describe())
        
        # Target distribution
        if 'Purchased' in self.df.columns:
            target_counts = self.df['Purchased'].value_counts()
            print(f"\nTarget distribution:")
            print(target_counts)
            print(f"Class balance: {target_counts[1]/len(self.df)*100:.1f}% purchased")
        
        return self.df
    
    def preprocess_data(self, feature_selection=True, scale_features=True):
        """Enhanced preprocessing with feature engineering and selection."""
        print("\n" + "=" * 50)
        print("PREPROCESSING DATA")
        print("=" * 50)
        
        # Handle missing values
        if self.df.isnull().sum().any():
            print("Handling missing values...")
            # Fill numerical columns with median
            num_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[num_cols] = self.df[num_cols].fillna(self.df[num_cols].median())
            
            # Fill categorical columns with mode
            cat_cols = self.df.select_dtypes(include=['object']).columns
            for col in cat_cols:
                if col != 'Purchased':
                    self.df[col] = self.df[col].fillna(self.df[col].mode()[0])
        
        # Encode categorical variables
        label_encoders = {}
        for col in self.df.select_dtypes(include=['object']).columns:
            if col != 'Purchased':  # Don't encode target
                le = LabelEncoder()
                self.df[col] = le.fit_transform(self.df[col].astype(str))
                label_encoders[col] = le
        
        # Feature engineering - create new features
        if 'Annual_Income' in self.df.columns and 'Spending_Score' in self.df.columns:
            self.df['Income_Spending_Ratio'] = self.df['Annual_Income'] / (self.df['Spending_Score'] + 1)
            self.df['High_Income'] = (self.df['Annual_Income'] > self.df['Annual_Income'].median()).astype(int)
            self.df['High_Spending'] = (self.df['Spending_Score'] > self.df['Spending_Score'].median()).astype(int)
            print("Created engineered features: Income_Spending_Ratio, High_Income, High_Spending")
        
        # Prepare features and target
        target_col = 'Purchased'
        feature_cols = [col for col in self.df.columns if col != target_col]
        
        X = self.df[feature_cols]
        y = self.df[target_col]
        
        # Feature selection
        if feature_selection and len(feature_cols) > 2:
            print(f"\nPerforming feature selection from {len(feature_cols)} features...")
            self.feature_selector = SelectKBest(f_classif, k=min(10, len(feature_cols)))
            X = self.feature_selector.fit_transform(X, y)
            selected_features = self.feature_selector.get_support()
            selected_feature_names = [feature_cols[i] for i in range(len(feature_cols)) if selected_features[i]]
            print(f"Selected features: {selected_feature_names}")
        
        # Train/test split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        if scale_features:
            self.X_train = self.scaler.fit_transform(self.X_train)
            self.X_test = self.scaler.transform(self.X_test)
            print("Features scaled using StandardScaler")
        
        print(f"Training set: {self.X_train.shape}, Test set: {self.X_test.shape}")
        
    def train_multiple_models(self):
        """Train and compare multiple classification algorithms."""
        print("\n" + "=" * 50)
        print("TRAINING MULTIPLE MODELS")
        print("=" * 50)
        
        # Define models to compare
        models_config = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(random_state=42),
            'Logistic Regression': LogisticRegression(random_state=42),
            'SVM': SVC(probability=True, random_state=42)
        }
        
        model_scores = {}
        
        for name, model in models_config.items():
            # Cross-validation
            cv_scores = cross_val_score(model, self.X_train, self.y_train, cv=5)
            
            # Train on full training set
            model.fit(self.X_train, self.y_train)
            
            # Predictions
            y_pred = model.predict(self.X_test)
            y_prob = model.predict_proba(self.X_test)[:, 1] if hasattr(model, "predict_proba") else None
            
            # Calculate metrics
            accuracy = accuracy_score(self.y_test, y_pred)
            auc = roc_auc_score(self.y_test, y_prob) if y_prob is not None else 0
            
            model_scores[name] = {
                'model': model,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'test_accuracy': accuracy,
                'test_auc': auc
            }
            
            self.models[name] = model
            
            print(f"{name}:")
            print(f"  CV Score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
            print(f"  Test Accuracy: {accuracy:.3f}")
            print(f"  Test AUC: {auc:.3f}")
            print()
        
        # Select best model based on CV score
        best_model_name = max(model_scores.keys(), key=lambda k: model_scores[k]['cv_mean'])
        self.best_model = self.models[best_model_name]
        print(f"Best model: {best_model_name}")
        
        return model_scores
    
    def hyperparameter_tuning(self, model_name='Random Forest'):
        """Perform hyperparameter tuning on the specified model."""
        print(f"\n" + "=" * 50)
        print(f"HYPERPARAMETER TUNING - {model_name}")
        print("=" * 50)
        
        if model_name == 'Random Forest':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            model = RandomForestClassifier(random_state=42)
        
        elif model_name == 'Gradient Boosting':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            }
            model = GradientBoostingClassifier(random_state=42)
        
        else:
            print(f"Hyperparameter tuning not configured for {model_name}")
            return None
        
        # Grid search
        grid_search = GridSearchCV(
            model, param_grid, cv=5, scoring='accuracy', n_jobs=-1
        )
        grid_search.fit(self.X_train, self.y_train)
        
        # Update best model
        self.best_model = grid_search.best_estimator_
        self.models[f'{model_name} (Tuned)'] = self.best_model
        
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best CV score: {grid_search.best_score_:.3f}")
        
        return grid_search.best_estimator_
    
    def evaluate_model(self, model=None):
        """Comprehensive model evaluation with multiple metrics and visualizations."""
        print("\n" + "=" * 50)
        print("MODEL EVALUATION")
        print("=" * 50)
        
        if model is None:
            model = self.best_model
        
        # Predictions
        y_pred = model.predict(self.X_test)
        y_prob = model.predict_proba(self.X_test)[:, 1] if hasattr(model, "predict_proba") else None
        
        # Basic metrics
        accuracy = accuracy_score(self.y_test, y_pred)
        print(f"Test Accuracy: {accuracy:.3f}")
        
        if y_prob is not None:
            auc = roc_auc_score(self.y_test, y_prob)
            print(f"AUC-ROC: {auc:.3f}")
        
        print(f"\nClassification Report:")
        print(classification_report(self.y_test, y_pred))
        
        # Confusion Matrix
        cm = confusion_matrix(self.y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(cm)
        
        return {'accuracy': accuracy, 'auc': auc if y_prob is not None else None}
    
    def create_visualizations(self):
        """Create comprehensive visualizations for model analysis."""
        print("\n" + "=" * 50)
        print("CREATING VISUALIZATIONS")
        print("=" * 50)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Enhanced Data Classifier Analysis', fontsize=16)
        
        # 1. Feature distributions
        if len(self.df.select_dtypes(include=[np.number]).columns) >= 2:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns[:2]
            for i, col in enumerate(numeric_cols):
                axes[0, i].hist(self.df[self.df['Purchased']==0][col], alpha=0.5, label='Not Purchased', color='red', bins=20)
                axes[0, i].hist(self.df[self.df['Purchased']==1][col], alpha=0.5, label='Purchased', color='green', bins=20)
                axes[0, i].set_title(f'{col} Distribution by Target')
                axes[0, i].set_xlabel(col)
                axes[0, i].set_ylabel('Frequency')
                axes[0, i].legend()
                axes[0, i].grid(True, alpha=0.3)
        
        # 2. Confusion Matrix Heatmap
        y_pred = self.best_model.predict(self.X_test)
        cm = confusion_matrix(self.y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1, 0])
        axes[1, 0].set_title('Confusion Matrix')
        axes[1, 0].set_xlabel('Predicted')
        axes[1, 0].set_ylabel('Actual')
        
        # 3. ROC Curve
        if hasattr(self.best_model, "predict_proba"):
            y_prob = self.best_model.predict_proba(self.X_test)[:, 1]
            fpr, tpr, _ = roc_curve(self.y_test, y_prob)
            auc = roc_auc_score(self.y_test, y_prob)
            
            axes[1, 1].plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.3f})', color='darkorange')
            axes[1, 1].plot([0, 1], [0, 1], 'k--', label='Random')
            axes[1, 1].set_xlabel('False Positive Rate')
            axes[1, 1].set_ylabel('True Positive Rate')
            axes[1, 1].set_title('ROC Curve')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Feature importance (if available)
        if hasattr(self.best_model, 'feature_importances_'):
            self.plot_feature_importance()
    
    def plot_feature_importance(self):
        """Plot feature importance for tree-based models."""
        if not hasattr(self.best_model, 'feature_importances_'):
            print("Model doesn't have feature importance")
            return
        
        # Get feature names
        if self.feature_selector is not None:
            feature_cols = [col for col in self.df.columns if col != 'Purchased']
            selected_features = self.feature_selector.get_support()
            feature_names = [feature_cols[i] for i in range(len(feature_cols)) if selected_features[i]]
        else:
            feature_names = [col for col in self.df.columns if col != 'Purchased']
        
        # Create importance plot
        importance = self.best_model.feature_importances_
        indices = np.argsort(importance)[::-1]
        
        plt.figure(figsize=(10, 6))
        plt.title('Feature Importance')
        plt.bar(range(len(importance)), importance[indices])
        plt.xticks(range(len(importance)), [feature_names[i] for i in indices], rotation=45)
        plt.xlabel('Features')
        plt.ylabel('Importance')
        plt.tight_layout()
        plt.show()
    
    def predict_new_customers(self, new_data):
        """Make predictions on new customer data with confidence scores."""
        print("\n" + "=" * 50)
        print("PREDICTING NEW CUSTOMERS")
        print("=" * 50)
        
        # Ensure new_data is DataFrame
        if isinstance(new_data, list):
            feature_cols = [col for col in self.df.columns if col != 'Purchased'][:len(new_data[0])]
            new_data = pd.DataFrame(new_data, columns=feature_cols)
        
        # Apply same preprocessing
        if self.feature_selector is not None:
            new_data_processed = self.feature_selector.transform(new_data)
        else:
            new_data_processed = new_data.values
        
        new_data_scaled = self.scaler.transform(new_data_processed)
        
        # Predictions
        predictions = self.best_model.predict(new_data_scaled)
        
        if hasattr(self.best_model, "predict_proba"):
            probabilities = self.best_model.predict_proba(new_data_scaled)[:, 1]
            
            for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
                print(f"Customer {i+1}: {dict(new_data.iloc[i])}")
                print(f"  → Prediction: {'Will Purchase' if pred == 1 else 'Will Not Purchase'}")
                print(f"  → Confidence: {prob:.3f}")
                print()
        else:
            for i, pred in enumerate(predictions):
                print(f"Customer {i+1}: {dict(new_data.iloc[i])}")
                print(f"  → Prediction: {'Will Purchase' if pred == 1 else 'Will Not Purchase'}")
                print()
        
        return predictions
    
    def run_complete_pipeline(self):
        """Run the complete enhanced machine learning pipeline."""
        print(" RUNNING ENHANCED DATA CLASSIFIER PIPELINE")
        print("=" * 60)
        
        # Step 1: Load and explore data
        self.load_and_explore_data()
        
        # Step 2: Preprocess data
        self.preprocess_data()
        
        # Step 3: Train multiple models
        model_scores = self.train_multiple_models()
        
        # Step 4: Hyperparameter tuning
        self.hyperparameter_tuning()
        
        # Step 5: Evaluate best model
        metrics = self.evaluate_model()
        
        # Step 6: Create visualizations
        self.create_visualizations()
        
        # Step 7: Test predictions on new customers
        new_customers = [
            [50000, 80],  # High income, high spending
            [30000, 30],  # Lower income, lower spending
            [70000, 60],  # High income, medium spending
        ]
        self.predict_new_customers(new_customers)
        
        print("\n PIPELINE COMPLETE!")
        return metrics

# Usage example
if __name__ == "__main__":
    # Initialize and run the enhanced classifier
    classifier = EnhancedDataClassifier("customer_data.csv")
    results = classifier.run_complete_pipeline()