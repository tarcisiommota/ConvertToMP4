import ffmpeg
import os
import shutil
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Diretório base onde o script será executado
base_dir = r"C:\Scripts\Conversores"
originals_dir = r"C:\Scripts\Conversores\Originais"

# Cria o diretório de "Originais" se não existir
os.makedirs(originals_dir, exist_ok=True)

# Função para realizar a conversão de um único arquivo
def convert_file(input_file, output_file, original_file_dir):
    try:
        # Mostra o progresso com a barra usando tqdm
        print(f"\nConvertendo {input_file} ...")
        with tqdm(total=100, desc=f'Convertendo {os.path.basename(input_file)}', unit='%') as pbar:
            (
                ffmpeg
                .input(input_file)
                .output(output_file, vcodec='libx264', acodec='aac', strict='experimental', audio_bitrate='192k')
                .run(overwrite_output=True)
            )
            pbar.update(100)  # Completa a barra
        
        # Move o arquivo original para o diretório "Originais"
        shutil.move(input_file, os.path.join(original_file_dir, os.path.basename(input_file)))
        
        # Retorna sucesso
        return input_file, True
    except Exception as e:
        # Retorna falha com a mensagem de erro
        return input_file, False, str(e)

# Função para processar os arquivos em paralelo
def process_files():
    # Lista para registrar resultados
    results = {"sucesso": [], "falha": []}
    
    # Usando ThreadPoolExecutor para conversão paralela
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        
        # Percorre todas as subpastas e arquivos
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".mkv"):
                    input_file = os.path.join(root, file)
                    output_file = os.path.join(root, file.replace(".mkv", ".mp4"))
                    
                    # Submissão de tarefas para o executor
                    futures.append(executor.submit(convert_file, input_file, output_file, originals_dir))
        
        # Monitorando as threads e registrando os resultados
        for future in as_completed(futures):
            result = future.result()
            if result[1]:  # Se teve sucesso
                results["sucesso"].append(result[0])
            else:  # Se falhou
                results["falha"].append((result[0], result[2]))
    
    return results

# Função para exibir o relatório final
def display_report(results):
    print("\n--- Relatório de Conversão ---")
    print(f"Total de arquivos convertidos com sucesso: {len(results['sucesso'])}")
    for success_file in results['sucesso']:
        print(f"  - {success_file}")
    
    if results["falha"]:
        print(f"\nTotal de arquivos que falharam: {len(results['falha'])}")
        for failed_file, error in results['falha']:
            print(f"  - {failed_file}: {error}")
    else:
        print("\nNenhuma falha ocorreu.")

# Função principal
def main():
    print("Iniciando o processo de conversão...\n")
    
    # Processa os arquivos e coleta os resultados
    results = process_files()
    
    # Exibe o relatório final
    display_report(results)
    
    print("\nProcesso concluído.")

if __name__ == "__main__":
    main()
