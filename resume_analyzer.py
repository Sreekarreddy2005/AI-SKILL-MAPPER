"""
Resume Analysis and Insights
===========================

This module provides analysis capabilities for processed resume data,
including skill frequency analysis, industry insights, and data visualization.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import json
from pathlib import Path
from typing import Dict, List, Tuple
import re


class ResumeAnalyzer:
    """
    Analyze processed resume data to extract insights and patterns.
    """
    
    def __init__(self, results: List[Dict]):
        """
        Initialize analyzer with processed resume results.
        
        Args:
            results (List[Dict]): List of processed resume dictionaries
        """
        self.results = results
        self.df = self._create_dataframe()
        
    def _create_dataframe(self) -> pd.DataFrame:
        """Create a pandas DataFrame from the results."""
        data = []
        
        for result in self.results:
            row = {
                'file_name': result['file_name'],
                'text_length': result['text_length'],
                'emails': len(result['entities']['emails']),
                'phones': len(result['entities']['phones']),
                'skills': result['entities']['skills'],
                'companies': result['entities']['companies'],
                'education': result['entities']['education'],
                'locations': result['entities']['locations'],
                'dates': result['entities']['dates']
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def get_skill_frequency(self, top_n: int = 20) -> Dict[str, int]:
        """
        Get frequency of skills across all resumes.
        
        Args:
            top_n (int): Number of top skills to return
            
        Returns:
            Dict[str, int]: Skill frequency dictionary
        """
        all_skills = []
        for skills in self.df['skills']:
            all_skills.extend(skills)
        
        skill_counter = Counter(all_skills)
        return dict(skill_counter.most_common(top_n))
    
    def get_company_frequency(self, top_n: int = 15) -> Dict[str, int]:
        """
        Get frequency of companies mentioned across resumes.
        
        Args:
            top_n (int): Number of top companies to return
            
        Returns:
            Dict[str, int]: Company frequency dictionary
        """
        all_companies = []
        for companies in self.df['companies']:
            all_companies.extend(companies)
        
        company_counter = Counter(all_companies)
        return dict(company_counter.most_common(top_n))
    
    def analyze_education_patterns(self) -> Dict[str, any]:
        """
        Analyze education patterns across resumes.
        
        Returns:
            Dict: Education analysis results
        """
        all_education = []
        for education in self.df['education']:
            all_education.extend(education)
        
        # Extract degree types
        degree_patterns = {
            'Bachelor': r'\b(?:Bachelor|B\.?S\.?|B\.?A\.?|B\.?Tech)\b',
            'Master': r'\b(?:Master|M\.?S\.?|M\.?A\.?|M\.?Tech|MBA)\b',
            'PhD': r'\b(?:PhD|Ph\.?D\.?|Doctorate)\b',
            'Certification': r'\b(?:Certified|Certification|Cert)\b'
        }
        
        degree_counts = {}
        for degree_type, pattern in degree_patterns.items():
            count = sum(1 for edu in all_education if re.search(pattern, edu, re.IGNORECASE))
            degree_counts[degree_type] = count
        
        return {
            'total_education_mentions': len(all_education),
            'degree_types': degree_counts,
            'unique_education': list(set(all_education))
        }
    
    def analyze_experience_levels(self) -> Dict[str, int]:
        """
        Analyze experience levels based on job titles and keywords.
        
        Returns:
            Dict[str, int]: Experience level distribution
        """
        experience_keywords = {
            'Junior': ['junior', 'entry', 'associate', 'trainee', 'fresher'],
            'Mid': ['mid', 'intermediate', 'experienced', 'professional'],
            'Senior': ['senior', 'lead', 'principal', 'architect'],
            'Manager': ['manager', 'director', 'head', 'vp', 'vice president'],
            'Consultant': ['consultant', 'advisor', 'specialist', 'expert']
        }
        
        # Combine all text from resumes for analysis
        all_text = ""
        for result in self.results:
            all_text += result['raw_text'].lower()
        
        level_counts = {}
        for level, keywords in experience_keywords.items():
            count = sum(all_text.count(keyword) for keyword in keywords)
            level_counts[level] = count
        
        return level_counts
    
    def get_contact_completeness(self) -> Dict[str, float]:
        """
        Analyze how complete contact information is across resumes.
        
        Returns:
            Dict[str, float]: Contact completeness percentages
        """
        total_resumes = len(self.df)
        
        has_email = (self.df['emails'] > 0).sum()
        has_phone = (self.df['phones'] > 0).sum()
        
        return {
            'email_completeness': (has_email / total_resumes) * 100,
            'phone_completeness': (has_phone / total_resumes) * 100,
            'total_analyzed': total_resumes
        }
    
    def generate_insights_report(self) -> Dict:
        """
        Generate a comprehensive insights report.
        
        Returns:
            Dict: Complete analysis report
        """
        report = {
            'dataset_overview': {
                'total_resumes': len(self.results),
                'avg_text_length': self.df['text_length'].mean(),
                'total_skills_found': sum(len(skills) for skills in self.df['skills'])
            },
            'skill_analysis': self.get_skill_frequency(15),
            'company_analysis': self.get_company_frequency(10),
            'education_analysis': self.analyze_education_patterns(),
            'experience_analysis': self.analyze_experience_levels(),
            'contact_analysis': self.get_contact_completeness()
        }
        
        return report
    
    def create_visualizations(self, save_path: str = None):
        """
        Create visualizations for the analysis.
        
        Args:
            save_path (str): Path to save plots (optional)
        """
        plt.style.use('default')
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Resume Dataset Analysis', fontsize=16, fontweight='bold')
        
        # 1. Top Skills
        skills_freq = self.get_skill_frequency(10)
        if skills_freq:
            axes[0, 0].barh(list(skills_freq.keys()), list(skills_freq.values()))
            axes[0, 0].set_title('Top 10 Skills')
            axes[0, 0].set_xlabel('Frequency')
        
        # 2. Text Length Distribution
        axes[0, 1].hist(self.df['text_length'], bins=20, alpha=0.7, color='skyblue')
        axes[0, 1].set_title('Resume Text Length Distribution')
        axes[0, 1].set_xlabel('Text Length (characters)')
        axes[0, 1].set_ylabel('Number of Resumes')
        
        # 3. Experience Levels
        exp_levels = self.analyze_experience_levels()
        if exp_levels:
            axes[1, 0].pie(list(exp_levels.values()), labels=list(exp_levels.keys()), 
                          autopct='%1.1f%%', startangle=90)
            axes[1, 0].set_title('Experience Level Distribution')
        
        # 4. Contact Completeness
        contact_comp = self.get_contact_completeness()
        contact_data = {
            'Email': contact_comp['email_completeness'],
            'Phone': contact_comp['phone_completeness']
        }
        axes[1, 1].bar(contact_data.keys(), contact_data.values(), color=['green', 'orange'])
        axes[1, 1].set_title('Contact Information Completeness')
        axes[1, 1].set_ylabel('Percentage (%)')
        axes[1, 1].set_ylim(0, 100)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualizations saved to: {save_path}")
        
        plt.show()
    
    def export_analysis(self, output_file: str = "resume_analysis.json"):
        """
        Export complete analysis to JSON file.
        
        Args:
            output_file (str): Output file path
        """
        report = self.generate_insights_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Analysis exported to: {output_file}")
        
        # Also create a summary CSV
        csv_file = output_file.replace('.json', '_summary.csv')
        
        # Create summary data for CSV
        summary_data = []
        for result in self.results:
            summary_data.append({
                'file_name': result['file_name'],
                'text_length': result['text_length'],
                'skills_count': len(result['entities']['skills']),
                'companies_count': len(result['entities']['companies']),
                'education_count': len(result['entities']['education']),
                'has_email': len(result['entities']['emails']) > 0,
                'has_phone': len(result['entities']['phones']) > 0
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(csv_file, index=False)
        print(f"Summary CSV exported to: {csv_file}")


def main():
    """Example usage of ResumeAnalyzer."""
    # Load sample results (you would load from actual processing)
    print("Resume Analyzer - Example Usage")
    print("=" * 40)
    print("This is a demonstration of the analysis capabilities.")
    print("To use with real data, process resumes first using ResumeProcessor.")
    
    # Example of what the analysis would show
    print("\nExample Analysis Features:")
    print("✅ Skill frequency analysis")
    print("✅ Company mention analysis") 
    print("✅ Education pattern recognition")
    print("✅ Experience level detection")
    print("✅ Contact completeness metrics")
    print("✅ Data visualization generation")
    print("✅ Export capabilities (JSON, CSV)")


if __name__ == "__main__":
    main()
