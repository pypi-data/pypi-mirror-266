from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate



class GenerateEvaluationQuestions:
    """
    A class to generate questions from a given text using an LLM.
    """

    def __init__(self, document:str, number_of_questions:int):
        self.document = document
        self.number_of_questions = number_of_questions

    def get_evaluation_questions(self):
        template = """
          You are an expert in analysing and finding questions for a assessment.
          You will be provided with the document, and you need to generate {num_of_questions} question from the document.
          The answer of the question so generated should be maximum 15-20 words only and directly available in the document.

          Document: {content}
          Questions:
          """
        # Make sure the questions are relevant and critical in examining the learning and understanding of the document.

        prompt = PromptTemplate(
          input_variables = ["num_of_questions","content"],
          template=template,
        )
        chain = LLMChain(llm=ChatOpenAI(model='gpt-3.5-turbo',temperature=0.2), prompt=prompt)
        ques = chain.invoke({"num_of_questions": self.number_of_questions, "content": self.document})
        ques_text = ques["text"]
        questions_list = ques_text.split('\n')
        # return [question.split('. ', 1)[1] for question in questions_list]
        return [question.split('. ', 1)[1] if '. ' in question else question for question in questions_list]
    



# from dotenv import load_dotenv
# load_dotenv()
# input_text =  """
# Title: Technology at the Dawn of the 21st Century

# As the world crossed the threshold into the 21st century, the landscape of technology underwent a profound transformation, reshaping the way we live, work, and interact. This era marked a pivotal moment in human history, characterized by rapid advancements in various fields of technology, revolutionizing communication, transportation, healthcare, and more. In this essay, we will explore the technological landscape at the dawn of the 21st century and its profound impact on society.

# One of the most significant technological breakthroughs of the early 21st century was the widespread adoption of the internet. The internet had already begun to gain traction in the late 20th century, but its influence truly exploded in the early years of the new millennium. With the advent of high-speed broadband connections, the internet became more accessible to people around the world, facilitating instant communication, access to information, and the rise of e-commerce.

# The proliferation of smartphones and mobile devices further accelerated the internet revolution. These portable gadgets empowered individuals to stay connected on the go, access a wealth of digital content, and engage with various online services. Social media platforms like Facebook, Twitter, and Instagram emerged as dominant forces, reshaping how people communicate, share information, and build communities.

# In addition to transforming communication, technology also revolutionized industries such as healthcare and transportation. The development of advanced medical imaging techniques, robotics, and telemedicine enabled more accurate diagnoses, minimally invasive surgeries, and remote patient monitoring. Similarly, innovations in transportation, such as electric vehicles and autonomous driving technology, promised to make travel safer, more efficient, and environmentally sustainable.

# The early 21st century also witnessed significant advancements in the field of artificial intelligence (AI) and machine learning. These technologies, once confined to the realm of science fiction, began to permeate various aspects of everyday life. AI-powered algorithms fueled personalized recommendations on streaming services, optimized logistics and supply chains, and even assisted in diagnosing diseases and predicting outcomes in healthcare.

# Furthermore, the rise of renewable energy technologies marked a crucial turning point in the fight against climate change. Solar panels, wind turbines, and other green energy sources gained traction as alternatives to fossil fuels, offering cleaner and more sustainable solutions to meet the world's growing energy demands. Governments and corporations increasingly invested in renewable energy infrastructure, signaling a shift towards a more environmentally conscious future.

# However, along with its myriad benefits, the rapid pace of technological advancement also brought about new challenges and ethical dilemmas. Concerns about data privacy, cybersecurity, and the ethical implications of AI algorithms became increasingly prominent. The digital divide widened, exacerbating inequalities as some communities struggled to access or afford the latest technologies.

# In conclusion, the dawn of the 21st century marked a period of unprecedented technological progress, reshaping nearly every aspect of human society. From the internet and mobile devices to artificial intelligence and renewable energy, the innovations of this era have transformed how we live, work, and interact with the world around us. As we continue to navigate the complexities of the digital age, it is essential to harness the potential of technology for the greater good while addressing its associated challenges and ensuring inclusivity and ethical responsibility.
# """
# get_question = GenerateEvaluationQuestions(input_text,2).get_evaluation_questions()
# print(get_question)