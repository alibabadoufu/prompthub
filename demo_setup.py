"""
Demo setup script for PromptFlow Studio.
This script creates sample data to help users get started quickly.
"""
import data_manager as dm
from utils import load_config


def setup_demo_data():
    """Create sample projects and prompts for demonstration."""
    print("🚀 Setting up demo data for PromptFlow Studio...")
    
    try:
        # Create sample projects
        print("\n📁 Creating sample projects...")
        
        # Customer Support Bot project
        try:
            project1_id = dm.create_project(
                "CustomerSupportBot",
                "AI assistant for handling customer support inquiries"
            )
            print(f"✅ Created project: CustomerSupportBot (ID: {project1_id})")
        except ValueError:
            print("ℹ️  Project 'CustomerSupportBot' already exists")
            project1 = dm.get_project_by_name("CustomerSupportBot")
            project1_id = project1["id"]
        
        # Content Creation project
        try:
            project2_id = dm.create_project(
                "ContentCreation",
                "Tools for automated content generation and editing"
            )
            print(f"✅ Created project: ContentCreation (ID: {project2_id})")
        except ValueError:
            print("ℹ️  Project 'ContentCreation' already exists")
            project2 = dm.get_project_by_name("ContentCreation")
            project2_id = project2["id"]
        
        # Create sample prompts for CustomerSupportBot
        print(f"\n📝 Creating sample prompts for CustomerSupportBot...")
        
        # Email Summarization prompt
        try:
            prompt1_id = dm.create_prompt(project1_id, "EmailSummarization")
            print(f"✅ Created prompt: EmailSummarization (ID: {prompt1_id})")
            
            # Add versions
            version1 = dm.save_prompt_version(
                prompt1_id,
                template_text="""Please summarize the following customer email in 3 bullet points:

{{customer_email}}

Focus on:
- Main issue or request
- Customer sentiment
- Urgency level""",
                model_name="Llama3 8B (Internal)",
                temperature=0.3,
                max_tokens=200,
                top_p=0.9,
                changelog="Initial version for email summarization"
            )
            
            version2 = dm.save_prompt_version(
                prompt1_id,
                template_text="""Analyze and summarize the following customer email:

{{customer_email}}

Provide a structured summary including:
- **Main Issue**: Brief description of the primary concern
- **Customer Sentiment**: Positive, Neutral, or Negative
- **Priority Level**: High, Medium, or Low
- **Suggested Action**: Recommended next step""",
                model_name="Llama3 8B (Internal)",
                temperature=0.2,
                max_tokens=300,
                top_p=0.95,
                changelog="Improved structure with sentiment analysis and priority assessment"
            )
            
            # Set version 2 as active
            dm.set_active_version(prompt1_id, version2)
            print(f"✅ Added {version2} versions to EmailSummarization (v{version2} is active)")
            
        except ValueError:
            print("ℹ️  Prompt 'EmailSummarization' already exists")
        
        # Response Generation prompt
        try:
            prompt2_id = dm.create_prompt(project1_id, "ResponseGeneration")
            print(f"✅ Created prompt: ResponseGeneration (ID: {prompt2_id})")
            
            version1 = dm.save_prompt_version(
                prompt2_id,
                template_text="""Generate a professional customer service response for the following inquiry:

**Customer Message:**
{{customer_message}}

**Context:**
- Customer Name: {{customer_name}}
- Issue Type: {{issue_type}}
- Priority: {{priority}}

Write a helpful, empathetic response that addresses their concern directly.""",
                model_name="Llama3 8B (Internal)",
                temperature=0.7,
                max_tokens=400,
                top_p=1.0,
                changelog="Initial response generation template"
            )
            
            dm.set_active_version(prompt2_id, version1)
            print(f"✅ Added version to ResponseGeneration (v{version1} is active)")
            
        except ValueError:
            print("ℹ️  Prompt 'ResponseGeneration' already exists")
        
        # Create sample prompts for ContentCreation
        print(f"\n✍️  Creating sample prompts for ContentCreation...")
        
        # Blog Post Outline prompt
        try:
            prompt3_id = dm.create_prompt(project2_id, "BlogPostOutline")
            print(f"✅ Created prompt: BlogPostOutline (ID: {prompt3_id})")
            
            version1 = dm.save_prompt_version(
                prompt3_id,
                template_text="""Create a comprehensive blog post outline for the following topic:

**Topic:** {{blog_topic}}
**Target Audience:** {{target_audience}}
**Word Count Goal:** {{word_count}} words

Generate an outline with:
1. Compelling headline
2. Introduction hook
3. 5-7 main sections with subpoints
4. Conclusion with call-to-action
5. SEO keyword suggestions

Make it engaging and actionable for the target audience.""",
                model_name="Llama3 8B (Internal)",
                temperature=0.8,
                max_tokens=500,
                top_p=0.95,
                changelog="Initial blog outline generation template"
            )
            
            dm.set_active_version(prompt3_id, version1)
            print(f"✅ Added version to BlogPostOutline (v{version1} is active)")
            
        except ValueError:
            print("ℹ️  Prompt 'BlogPostOutline' already exists")
        
        # Social Media Caption prompt
        try:
            prompt4_id = dm.create_prompt(project2_id, "SocialMediaCaption")
            print(f"✅ Created prompt: SocialMediaCaption (ID: {prompt4_id})")
            
            version1 = dm.save_prompt_version(
                prompt4_id,
                template_text="""Create an engaging social media caption for {{platform}}:

**Content Description:** {{content_description}}
**Brand Voice:** {{brand_voice}}
**Call-to-Action:** {{cta_type}}

Requirements:
- Keep it concise and platform-appropriate
- Include relevant hashtags (3-5)
- Match the specified brand voice
- Include the requested call-to-action
- Make it shareable and engaging""",
                model_name="Llama3 8B (Internal)",
                temperature=0.9,
                max_tokens=200,
                top_p=1.0,
                changelog="Social media caption generator for multiple platforms"
            )
            
            dm.set_active_version(prompt4_id, version1)
            print(f"✅ Added version to SocialMediaCaption (v{version1} is active)")
            
        except ValueError:
            print("ℹ️  Prompt 'SocialMediaCaption' already exists")
        
        print("\n🎉 Demo data setup complete!")
        print("\n📊 Summary:")
        print("- 2 projects created: CustomerSupportBot, ContentCreation")
        print("- 4 prompts created with active versions")
        print("- Ready to test variable substitution and API access")
        
        print("\n🧪 Try these example variable inputs:")
        print("\nFor EmailSummarization:")
        print('{"customer_email": "Hi, I ordered a laptop last week but it arrived with a cracked screen. I need a replacement ASAP as I need it for work. This is very frustrating!"}')
        
        print("\nFor ResponseGeneration:")
        print('{"customer_message": "My order hasn\'t arrived yet", "customer_name": "John Smith", "issue_type": "Delivery Delay", "priority": "Medium"}')
        
        print("\nFor BlogPostOutline:")
        print('{"blog_topic": "10 Tips for Remote Work Productivity", "target_audience": "Remote workers and freelancers", "word_count": "1500"}')
        
        print("\nFor SocialMediaCaption:")
        print('{"platform": "Instagram", "content_description": "New product launch - wireless headphones", "brand_voice": "Friendly and tech-savvy", "cta_type": "Visit website"}')
        
        print("\n🚀 Launch the app with: python app.py")
        
    except Exception as e:
        print(f"❌ Error setting up demo data: {e}")
        return False
    
    return True


if __name__ == "__main__":
    setup_demo_data()